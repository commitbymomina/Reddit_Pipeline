import os
import logging
from datetime import datetime, timezone  

import praw
import psycopg2
from psycopg2 import pool

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global DB connection pool
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = psycopg2.pool.SimpleConnectionPool(
                1, 5,
                host=os.environ['DB_HOST'],
                database=os.environ['DB_NAME'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD'],
                connect_timeout=5
            )
            logger.info("Initialized DB connection pool")
        except Exception as e:
            logger.error(f"Failed to initialize DB pool: {e}")
            raise

def get_db_connection():
    if db_pool is None:
        init_db_pool()
    return db_pool.getconn()

def release_db_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def lambda_handler(event, context):
    # Validate required environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'SUBREDDITS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise EnvironmentError(f"Missing env vars: {missing_vars}")

    post_limit = int(os.getenv('POST_LIMIT', '20'))
    comment_limit = int(os.getenv('COMMENT_LIMIT', '5'))

    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent="script:PostHarvester:v.1.5 (by u/InsightMiner_6258; +uuid:38f7c9f2-994e-47e1-a341-f7e3b92b301d)",
        username=os.environ['REDDIT_USERNAME'],
        password=os.environ['REDDIT_PASSWORD']
    )

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        subreddits = [s.strip() for s in os.environ['SUBREDDITS'].split(',')]
        for subreddit in subreddits:
            process_subreddit(reddit, cursor, subreddit, post_limit, comment_limit)
            conn.commit()

    except Exception as e:
        logger.error(f"Error during Lambda execution: {e}", exc_info=True)
        raise
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

def process_subreddit(reddit, cursor, subreddit, post_limit, comment_limit):
    logger.info(f"Processing r/{subreddit}...")

    try:
        for post in reddit.subreddit(subreddit).top(time_filter='day', limit=post_limit):
            post_id = f"t3_{post.id}"
            author_str = str(post.author) if post.author else '[deleted]'
            created_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)  # Updated to use fromtimestamp

            cursor.execute("""
                INSERT INTO reddit_posts (
                    post_id, title, selftext, author, score,
                    upvote_ratio, url, created_utc, subreddit, is_original_content, last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (post_id)
                DO UPDATE SET
                    score = EXCLUDED.score,
                    upvote_ratio = EXCLUDED.upvote_ratio,
                    last_updated = NOW()
            """, (
                post_id, post.title, post.selftext, author_str,
                post.score, post.upvote_ratio, post.url,
                created_time, subreddit, post.is_original_content
            ))

            post.comments.replace_more(limit=0)
            for comment in post.comments.list()[:comment_limit]:
                comment_id = f"t1_{comment.id}"
                comment_author = str(comment.author) if comment.author else '[deleted]'
                comment_created = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)  # Updated to use fromtimestamp

                cursor.execute("""
                    INSERT INTO reddit_comments (
                        comment_id, post_id, body, author, score, created_utc, last_updated
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (comment_id)
                    DO UPDATE SET
                        score = EXCLUDED.score,
                        last_updated = NOW()
                """, (
                    comment_id, post_id, comment.body,
                    comment_author, comment.score, comment_created
                ))

        logger.info(f"Completed processing r/{subreddit}")

    except praw.exceptions.RedditAPIException as api_err:
        logger.warning(f"Reddit API error for r/{subreddit}: {api_err}")
    except Exception as e:
        logger.error(f"Unexpected error processing r/{subreddit}: {e}", exc_info=True)
        raise
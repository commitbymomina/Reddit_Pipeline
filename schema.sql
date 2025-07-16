CREATE TABLE IF NOT EXISTS public.reddit_comments
(
    comment_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
    post_id character varying(20) COLLATE pg_catalog."default",
    body text COLLATE pg_catalog."default",
    author character varying(50) COLLATE pg_catalog."default",
    score integer,
    created_utc timestamp with time zone,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reddit_comments_pkey PRIMARY KEY (comment_id)
);

CREATE TABLE IF NOT EXISTS public.reddit_posts
(
    post_id character varying(20) COLLATE pg_catalog."default" NOT NULL,
    title text COLLATE pg_catalog."default" NOT NULL,
    selftext text COLLATE pg_catalog."default",
    author character varying(50) COLLATE pg_catalog."default",
    score integer,
    upvote_ratio double precision,
    url text COLLATE pg_catalog."default",
    created_utc timestamp with time zone,
    subreddit character varying(20) COLLATE pg_catalog."default" NOT NULL,
    is_original_content boolean,
    inserted_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT reddit_posts_pkey PRIMARY KEY (post_id)
);

ALTER TABLE IF EXISTS public.reddit_comments
    ADD CONSTRAINT reddit_comments_post_id_fkey FOREIGN KEY (post_id)
    REFERENCES public.reddit_posts (post_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;
CREATE INDEX IF NOT EXISTS idx_comments_post_id
    ON public.reddit_comments(post_id);

END;
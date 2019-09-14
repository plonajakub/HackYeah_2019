CREATE TABLE readers
(
    id         integer primary key,
    first_name varchar(255),
    last_name  varchar(255),
    username   varchar(255)
);

CREATE TABLE articles
(
    guid varchar(36) primary key,
    url  text not null
);

CREATE TABLE articles_tags
(
    article varchar(36) not null,
    tag varchar(255) not null,
    foreign key (article) references articles (guid)
);

CREATE TABLE links_for_readers
(
    guid    varchar(36) primary key,
    reader  integer     not null,
    article varchar(36) not null,
    visited integer     not null default 0, -- >1 -- link visited more than once. :)
    foreign key (reader) references readers (id),
    foreign key (article) references articles (guid)
);
--
-- PostgreSQL database dump
--

\restrict wy8XUyO9pjeALOqStbzVMlS54DMDCgh8fHtaMrR1W4oXA3NaP8zXdMl87oB4RaH

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: annotation_tag_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.annotation_tag_entity (
    id character varying(16) NOT NULL,
    name character varying(24) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.annotation_tag_entity OWNER TO openagile;

--
-- Name: auth_identity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.auth_identity (
    "userId" uuid,
    "providerId" character varying(64) NOT NULL,
    "providerType" character varying(32) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.auth_identity OWNER TO openagile;

--
-- Name: auth_provider_sync_history; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.auth_provider_sync_history (
    id integer NOT NULL,
    "providerType" character varying(32) NOT NULL,
    "runMode" text NOT NULL,
    status text NOT NULL,
    "startedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "endedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    scanned integer NOT NULL,
    created integer NOT NULL,
    updated integer NOT NULL,
    disabled integer NOT NULL,
    error text
);


ALTER TABLE public.auth_provider_sync_history OWNER TO openagile;

--
-- Name: auth_provider_sync_history_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

CREATE SEQUENCE public.auth_provider_sync_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_provider_sync_history_id_seq OWNER TO openagile;

--
-- Name: auth_provider_sync_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openagile
--

ALTER SEQUENCE public.auth_provider_sync_history_id_seq OWNED BY public.auth_provider_sync_history.id;


--
-- Name: credentials_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.credentials_entity (
    name character varying(128) NOT NULL,
    data text NOT NULL,
    type character varying(128) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    id character varying(36) NOT NULL,
    "isManaged" boolean DEFAULT false NOT NULL
);


ALTER TABLE public.credentials_entity OWNER TO openagile;

--
-- Name: data_table; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.data_table (
    id character varying(36) NOT NULL,
    name character varying(128) NOT NULL,
    "projectId" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.data_table OWNER TO openagile;

--
-- Name: data_table_column; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.data_table_column (
    id character varying(36) NOT NULL,
    name character varying(128) NOT NULL,
    type character varying(32) NOT NULL,
    index integer NOT NULL,
    "dataTableId" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.data_table_column OWNER TO openagile;

--
-- Name: COLUMN data_table_column.type; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.data_table_column.type IS 'Expected: string, number, boolean, or date (not enforced as a constraint)';


--
-- Name: COLUMN data_table_column.index; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.data_table_column.index IS 'Column order, starting from 0 (0 = first column)';


--
-- Name: event_destinations; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.event_destinations (
    id uuid NOT NULL,
    destination jsonb NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.event_destinations OWNER TO openagile;

--
-- Name: execution_annotation_tags; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.execution_annotation_tags (
    "annotationId" integer NOT NULL,
    "tagId" character varying(24) NOT NULL
);


ALTER TABLE public.execution_annotation_tags OWNER TO openagile;

--
-- Name: execution_annotations; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.execution_annotations (
    id integer NOT NULL,
    "executionId" integer NOT NULL,
    vote character varying(6),
    note text,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.execution_annotations OWNER TO openagile;

--
-- Name: execution_annotations_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

CREATE SEQUENCE public.execution_annotations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.execution_annotations_id_seq OWNER TO openagile;

--
-- Name: execution_annotations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openagile
--

ALTER SEQUENCE public.execution_annotations_id_seq OWNED BY public.execution_annotations.id;


--
-- Name: execution_data; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.execution_data (
    "executionId" integer NOT NULL,
    "workflowData" json NOT NULL,
    data text NOT NULL
);


ALTER TABLE public.execution_data OWNER TO openagile;

--
-- Name: execution_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.execution_entity (
    id integer NOT NULL,
    finished boolean NOT NULL,
    mode character varying NOT NULL,
    "retryOf" character varying,
    "retrySuccessId" character varying,
    "startedAt" timestamp(3) with time zone,
    "stoppedAt" timestamp(3) with time zone,
    "waitTill" timestamp(3) with time zone,
    status character varying NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    "deletedAt" timestamp(3) with time zone,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.execution_entity OWNER TO openagile;

--
-- Name: execution_entity_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

CREATE SEQUENCE public.execution_entity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.execution_entity_id_seq OWNER TO openagile;

--
-- Name: execution_entity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openagile
--

ALTER SEQUENCE public.execution_entity_id_seq OWNED BY public.execution_entity.id;


--
-- Name: execution_metadata; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.execution_metadata (
    id integer NOT NULL,
    "executionId" integer NOT NULL,
    key character varying(255) NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.execution_metadata OWNER TO openagile;

--
-- Name: execution_metadata_temp_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

CREATE SEQUENCE public.execution_metadata_temp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.execution_metadata_temp_id_seq OWNER TO openagile;

--
-- Name: execution_metadata_temp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openagile
--

ALTER SEQUENCE public.execution_metadata_temp_id_seq OWNED BY public.execution_metadata.id;


--
-- Name: folder; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.folder (
    id character varying(36) NOT NULL,
    name character varying(128) NOT NULL,
    "parentFolderId" character varying(36),
    "projectId" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.folder OWNER TO openagile;

--
-- Name: folder_tag; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.folder_tag (
    "folderId" character varying(36) NOT NULL,
    "tagId" character varying(36) NOT NULL
);


ALTER TABLE public.folder_tag OWNER TO openagile;

--
-- Name: insights_by_period; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.insights_by_period (
    id integer NOT NULL,
    "metaId" integer NOT NULL,
    type integer NOT NULL,
    value bigint NOT NULL,
    "periodUnit" integer NOT NULL,
    "periodStart" timestamp(0) with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.insights_by_period OWNER TO openagile;

--
-- Name: COLUMN insights_by_period.type; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.insights_by_period.type IS '0: time_saved_minutes, 1: runtime_milliseconds, 2: success, 3: failure';


--
-- Name: COLUMN insights_by_period."periodUnit"; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.insights_by_period."periodUnit" IS '0: hour, 1: day, 2: week';


--
-- Name: insights_by_period_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

ALTER TABLE public.insights_by_period ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.insights_by_period_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: insights_metadata; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.insights_metadata (
    "metaId" integer NOT NULL,
    "workflowId" character varying(16),
    "projectId" character varying(36),
    "workflowName" character varying(128) NOT NULL,
    "projectName" character varying(255) NOT NULL
);


ALTER TABLE public.insights_metadata OWNER TO openagile;

--
-- Name: insights_metadata_metaId_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

ALTER TABLE public.insights_metadata ALTER COLUMN "metaId" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public."insights_metadata_metaId_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: insights_raw; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.insights_raw (
    id integer NOT NULL,
    "metaId" integer NOT NULL,
    type integer NOT NULL,
    value bigint NOT NULL,
    "timestamp" timestamp(0) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.insights_raw OWNER TO openagile;

--
-- Name: COLUMN insights_raw.type; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.insights_raw.type IS '0: time_saved_minutes, 1: runtime_milliseconds, 2: success, 3: failure';


--
-- Name: insights_raw_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

ALTER TABLE public.insights_raw ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.insights_raw_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: installed_nodes; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.installed_nodes (
    name character varying(200) NOT NULL,
    type character varying(200) NOT NULL,
    "latestVersion" integer DEFAULT 1 NOT NULL,
    package character varying(241) NOT NULL
);


ALTER TABLE public.installed_nodes OWNER TO openagile;

--
-- Name: installed_packages; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.installed_packages (
    "packageName" character varying(214) NOT NULL,
    "installedVersion" character varying(50) NOT NULL,
    "authorName" character varying(70),
    "authorEmail" character varying(70),
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.installed_packages OWNER TO openagile;

--
-- Name: invalid_auth_token; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.invalid_auth_token (
    token character varying(512) NOT NULL,
    "expiresAt" timestamp(3) with time zone NOT NULL
);


ALTER TABLE public.invalid_auth_token OWNER TO openagile;

--
-- Name: migrations; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.migrations (
    id integer NOT NULL,
    "timestamp" bigint NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.migrations OWNER TO openagile;

--
-- Name: migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: openagile
--

CREATE SEQUENCE public.migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.migrations_id_seq OWNER TO openagile;

--
-- Name: migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openagile
--

ALTER SEQUENCE public.migrations_id_seq OWNED BY public.migrations.id;


--
-- Name: processed_data; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.processed_data (
    "workflowId" character varying(36) NOT NULL,
    context character varying(255) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    value text NOT NULL
);


ALTER TABLE public.processed_data OWNER TO openagile;

--
-- Name: project; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.project (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    icon json,
    description character varying(512)
);


ALTER TABLE public.project OWNER TO openagile;

--
-- Name: project_relation; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.project_relation (
    "projectId" character varying(36) NOT NULL,
    "userId" uuid NOT NULL,
    role character varying NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.project_relation OWNER TO openagile;

--
-- Name: role; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.role (
    slug character varying(128) NOT NULL,
    "displayName" text,
    description text,
    "roleType" text,
    "systemRole" boolean DEFAULT false NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.role OWNER TO openagile;

--
-- Name: COLUMN role.slug; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.role.slug IS 'Unique identifier of the role for example: "global:owner"';


--
-- Name: COLUMN role."displayName"; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.role."displayName" IS 'Name used to display in the UI';


--
-- Name: COLUMN role.description; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.role.description IS 'Text describing the scope in more detail of users';


--
-- Name: COLUMN role."roleType"; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.role."roleType" IS 'Type of the role, e.g., global, project, or workflow';


--
-- Name: COLUMN role."systemRole"; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.role."systemRole" IS 'Indicates if the role is managed by the system and cannot be edited';


--
-- Name: role_scope; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.role_scope (
    "roleSlug" character varying(128) NOT NULL,
    "scopeSlug" character varying(128) NOT NULL
);


ALTER TABLE public.role_scope OWNER TO openagile;

--
-- Name: scope; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.scope (
    slug character varying(128) NOT NULL,
    "displayName" text,
    description text
);


ALTER TABLE public.scope OWNER TO openagile;

--
-- Name: COLUMN scope.slug; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.scope.slug IS 'Unique identifier of the scope for example: "project:create"';


--
-- Name: COLUMN scope."displayName"; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.scope."displayName" IS 'Name used to display in the UI';


--
-- Name: COLUMN scope.description; Type: COMMENT; Schema: public; Owner: openagile
--

COMMENT ON COLUMN public.scope.description IS 'Text describing the scope in more detail of users';


--
-- Name: settings; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.settings (
    key character varying(255) NOT NULL,
    value text NOT NULL,
    "loadOnStartup" boolean DEFAULT false NOT NULL
);


ALTER TABLE public.settings OWNER TO openagile;

--
-- Name: shared_credentials; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.shared_credentials (
    "credentialsId" character varying(36) NOT NULL,
    "projectId" character varying(36) NOT NULL,
    role text NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.shared_credentials OWNER TO openagile;

--
-- Name: shared_workflow; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.shared_workflow (
    "workflowId" character varying(36) NOT NULL,
    "projectId" character varying(36) NOT NULL,
    role text NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.shared_workflow OWNER TO openagile;

--
-- Name: tag_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.tag_entity (
    name character varying(24) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    id character varying(36) NOT NULL
);


ALTER TABLE public.tag_entity OWNER TO openagile;

--
-- Name: test_case_execution; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.test_case_execution (
    id character varying(36) NOT NULL,
    "testRunId" character varying(36) NOT NULL,
    "executionId" integer,
    status character varying NOT NULL,
    "runAt" timestamp(3) with time zone,
    "completedAt" timestamp(3) with time zone,
    "errorCode" character varying,
    "errorDetails" json,
    metrics json,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    inputs json,
    outputs json
);


ALTER TABLE public.test_case_execution OWNER TO openagile;

--
-- Name: test_run; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.test_run (
    id character varying(36) NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    status character varying NOT NULL,
    "errorCode" character varying,
    "errorDetails" json,
    "runAt" timestamp(3) with time zone,
    "completedAt" timestamp(3) with time zone,
    metrics json,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE public.test_run OWNER TO openagile;

--
-- Name: user; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public."user" (
    id uuid DEFAULT uuid_in((OVERLAY(OVERLAY(md5((((random())::text || ':'::text) || (clock_timestamp())::text)) PLACING '4'::text FROM 13) PLACING to_hex((floor(((random() * (((11 - 8) + 1))::double precision) + (8)::double precision)))::integer) FROM 17))::cstring) NOT NULL,
    email character varying(255),
    "firstName" character varying(32),
    "lastName" character varying(32),
    password character varying(255),
    "personalizationAnswers" json,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    settings json,
    disabled boolean DEFAULT false NOT NULL,
    "mfaEnabled" boolean DEFAULT false NOT NULL,
    "mfaSecret" text,
    "mfaRecoveryCodes" text,
    "lastActiveAt" date,
    "roleSlug" character varying(128) DEFAULT 'global:member'::character varying NOT NULL
);


ALTER TABLE public."user" OWNER TO openagile;

--
-- Name: user_api_keys; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.user_api_keys (
    id character varying(36) NOT NULL,
    "userId" uuid NOT NULL,
    label character varying(100) NOT NULL,
    "apiKey" character varying NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    scopes json,
    audience character varying DEFAULT 'public-api'::character varying NOT NULL
);


ALTER TABLE public.user_api_keys OWNER TO openagile;

--
-- Name: variables; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.variables (
    key character varying(50) NOT NULL,
    type character varying(50) DEFAULT 'string'::character varying NOT NULL,
    value character varying(255),
    id character varying(36) NOT NULL,
    "projectId" character varying(36)
);


ALTER TABLE public.variables OWNER TO openagile;

--
-- Name: webhook_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.webhook_entity (
    "webhookPath" character varying NOT NULL,
    method character varying NOT NULL,
    node character varying NOT NULL,
    "webhookId" character varying,
    "pathLength" integer,
    "workflowId" character varying(36) NOT NULL
);


ALTER TABLE public.webhook_entity OWNER TO openagile;

--
-- Name: workflow_entity; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.workflow_entity (
    name character varying(128) NOT NULL,
    active boolean NOT NULL,
    nodes json NOT NULL,
    connections json NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    settings json,
    "staticData" json,
    "pinData" json,
    "versionId" character(36),
    "triggerCount" integer DEFAULT 0 NOT NULL,
    id character varying(36) NOT NULL,
    meta json,
    "parentFolderId" character varying(36) DEFAULT NULL::character varying,
    "isArchived" boolean DEFAULT false NOT NULL
);


ALTER TABLE public.workflow_entity OWNER TO openagile;

--
-- Name: workflow_history; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.workflow_history (
    "versionId" character varying(36) NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    authors character varying(255) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    nodes json NOT NULL,
    connections json NOT NULL
);


ALTER TABLE public.workflow_history OWNER TO openagile;

--
-- Name: workflow_statistics; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.workflow_statistics (
    count integer DEFAULT 0,
    "latestEvent" timestamp(3) with time zone,
    name character varying(128) NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    "rootCount" integer DEFAULT 0
);


ALTER TABLE public.workflow_statistics OWNER TO openagile;

--
-- Name: workflows_tags; Type: TABLE; Schema: public; Owner: openagile
--

CREATE TABLE public.workflows_tags (
    "workflowId" character varying(36) NOT NULL,
    "tagId" character varying(36) NOT NULL
);


ALTER TABLE public.workflows_tags OWNER TO openagile;

--
-- Name: auth_provider_sync_history id; Type: DEFAULT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.auth_provider_sync_history ALTER COLUMN id SET DEFAULT nextval('public.auth_provider_sync_history_id_seq'::regclass);


--
-- Name: execution_annotations id; Type: DEFAULT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotations ALTER COLUMN id SET DEFAULT nextval('public.execution_annotations_id_seq'::regclass);


--
-- Name: execution_entity id; Type: DEFAULT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_entity ALTER COLUMN id SET DEFAULT nextval('public.execution_entity_id_seq'::regclass);


--
-- Name: execution_metadata id; Type: DEFAULT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_metadata ALTER COLUMN id SET DEFAULT nextval('public.execution_metadata_temp_id_seq'::regclass);


--
-- Name: migrations id; Type: DEFAULT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.migrations ALTER COLUMN id SET DEFAULT nextval('public.migrations_id_seq'::regclass);


--
-- Data for Name: annotation_tag_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.annotation_tag_entity (id, name, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: auth_identity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.auth_identity ("userId", "providerId", "providerType", "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: auth_provider_sync_history; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.auth_provider_sync_history (id, "providerType", "runMode", status, "startedAt", "endedAt", scanned, created, updated, disabled, error) FROM stdin;
\.


--
-- Data for Name: credentials_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.credentials_entity (name, data, type, "createdAt", "updatedAt", id, "isManaged") FROM stdin;
Groq account	U2FsdGVkX18GUEQkc0lT/ojJFUcuLhY3PDrP772xc5jH1wjfOi/iC3Yj+ol8eVFgSFyar8fqUnFJYPfRYUfPvSVqFCXs50m9nSyVPRl3vLmt3QkEZzZD3t4H6TiUFVxw	groqApi	2025-10-29 21:27:28.454+00	2025-10-29 21:27:28.452+00	7TdeyWV7he2JL6fk	f
Google Sheets account	U2FsdGVkX1+6qSbV4fB4dXJTtI6Yrns18wriiEVloz2X3cAxrrvzkO9sVVXNc/IhCtJ2rExdU/Kzp553vBeJbG6OBrIxiGav/InfPgAmQEabD6JOrzJSgH9X2oJh26MY85dF31+TK8YY3cqE2u2TJ96DOb1HUYjSBPi8/9vFszFOETDk/Qcj1zir8HrC/V8uB+ZS0PTfhD5nrMdpqPCoip0VcZMKtGknuBgJMamgOqsUQ6ddtoBfc+uhTcMtFSsj69oOzdQl/xT2pi4C8Fgsd82slV0EAF0qgwMDbOHWl5EDVc2g+mArx7QwFotpqNKEey0ZiBbXl7tzpUyTMOyp0X4L1Oyyx5O4yfETZYLNJE6NLJZh6Jg9cH1j48KB2GOnsNHffyNrHunqsRqwX17RkPpxhmca3+2xSVODZ7NnmO32qDNo+Wpojb3SCv4Ym7kNV7s4tXiA2yrMSooCH2TTNQn5uInGbc/bMt15xRz+74To55yUDhe5iIH8n2+r8CWi6DifnRXDNBmzdhRmebq9WbR87MqKoQ3/MYUCsrH7G4Xfrgmj8FuqFwUZaHu7RaoD7AIqcKfqfjq6SAMxljCcKV+BpRagcsDxlFRYBJrhpmZ+RiLNMx3+dL/4FCsBMOrs0vqD6LGECuTxgEcS5zNBZt06/VK03PFLHRIZc1IRBPe4/WbvrvFIeMfVJi20ioMgHIde2yQdo0XuRhurDfr3O0S8KHWtQEC284uBuoRYMzKKpAKUz/Az1IzJoXlMzc+uz4rehCdtoKBLElbBtwRK9Z4kvo+U4lgQ3gQzx/sIh0D+PWZYjbCMsEqC3DoS9X39P7f41ZulrTq4pf6CTdxTaDsBlQdznSBsNe1+0KSae6o0NCg0TiLnMefjiEfV1evkTL53M1E0wwBXk1iuGXTLuG7+dGElEnfmXPPvmDzYoM1Z2FXq6A7amU2XRMH6sJnuKwSAipVq19jlzU0F1MoeD/WcySTyuxMogTc8c5L0KnMxqm9yUV4L5Wlo9O25wUaTsd/lxmUxtWxCmmXEp72eHzO2SRQ7AG/3Cau4otquj9yYCBjZUZrpux9YHvOuIMc9oRlT1d4g93F0Enu2fi/Xr38gOJxNnwNi/p1K/s3EEM6oyJy8AyXPusEtfErrfuxbOnxdvJBBGUzTZujBmv9d8GG2lUXKAjAwwBVW1PydD/i/EcXckSYsZRTol62nRfLAdIHoJwQ5jSsUhAX104wpHuSP8tgc6J8aOPEmWhY9/2pXmXkf2qysJhrffBd6sT0a	googleSheetsOAuth2Api	2025-11-08 17:47:04.233+00	2025-11-08 19:10:15.557+00	YGaPHefyc9NONFfU	f
\.


--
-- Data for Name: data_table; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.data_table (id, name, "projectId", "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: data_table_column; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.data_table_column (id, name, type, index, "dataTableId", "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: event_destinations; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.event_destinations (id, destination, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: execution_annotation_tags; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.execution_annotation_tags ("annotationId", "tagId") FROM stdin;
\.


--
-- Data for Name: execution_annotations; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.execution_annotations (id, "executionId", vote, note, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: execution_data; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.execution_data ("executionId", "workflowData", data) FROM stdin;
\.


--
-- Data for Name: execution_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.execution_entity (id, finished, mode, "retryOf", "retrySuccessId", "startedAt", "stoppedAt", "waitTill", status, "workflowId", "deletedAt", "createdAt") FROM stdin;
\.


--
-- Data for Name: execution_metadata; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.execution_metadata (id, "executionId", key, value) FROM stdin;
\.


--
-- Data for Name: folder; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.folder (id, name, "parentFolderId", "projectId", "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: folder_tag; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.folder_tag ("folderId", "tagId") FROM stdin;
\.


--
-- Data for Name: insights_by_period; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.insights_by_period (id, "metaId", type, value, "periodUnit", "periodStart") FROM stdin;
\.


--
-- Data for Name: insights_metadata; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.insights_metadata ("metaId", "workflowId", "projectId", "workflowName", "projectName") FROM stdin;
\.


--
-- Data for Name: insights_raw; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.insights_raw (id, "metaId", type, value, "timestamp") FROM stdin;
\.


--
-- Data for Name: installed_nodes; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.installed_nodes (name, type, "latestVersion", package) FROM stdin;
\.


--
-- Data for Name: installed_packages; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.installed_packages ("packageName", "installedVersion", "authorName", "authorEmail", "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: invalid_auth_token; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.invalid_auth_token (token, "expiresAt") FROM stdin;
\.


--
-- Data for Name: migrations; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.migrations (id, "timestamp", name) FROM stdin;
1	1587669153312	InitialMigration1587669153312
2	1589476000887	WebhookModel1589476000887
3	1594828256133	CreateIndexStoppedAt1594828256133
4	1607431743768	MakeStoppedAtNullable1607431743768
5	1611144599516	AddWebhookId1611144599516
6	1617270242566	CreateTagEntity1617270242566
7	1620824779533	UniqueWorkflowNames1620824779533
8	1626176912946	AddwaitTill1626176912946
9	1630419189837	UpdateWorkflowCredentials1630419189837
10	1644422880309	AddExecutionEntityIndexes1644422880309
11	1646834195327	IncreaseTypeVarcharLimit1646834195327
12	1646992772331	CreateUserManagement1646992772331
13	1648740597343	LowerCaseUserEmail1648740597343
14	1652254514002	CommunityNodes1652254514002
15	1652367743993	AddUserSettings1652367743993
16	1652905585850	AddAPIKeyColumn1652905585850
17	1654090467022	IntroducePinData1654090467022
18	1658932090381	AddNodeIds1658932090381
19	1659902242948	AddJsonKeyPinData1659902242948
20	1660062385367	CreateCredentialsUserRole1660062385367
21	1663755770893	CreateWorkflowsEditorRole1663755770893
22	1664196174001	WorkflowStatistics1664196174001
23	1665484192212	CreateCredentialUsageTable1665484192212
24	1665754637025	RemoveCredentialUsageTable1665754637025
25	1669739707126	AddWorkflowVersionIdColumn1669739707126
26	1669823906995	AddTriggerCountColumn1669823906995
27	1671535397530	MessageEventBusDestinations1671535397530
28	1671726148421	RemoveWorkflowDataLoadedFlag1671726148421
29	1673268682475	DeleteExecutionsWithWorkflows1673268682475
30	1674138566000	AddStatusToExecutions1674138566000
31	1674509946020	CreateLdapEntities1674509946020
32	1675940580449	PurgeInvalidWorkflowConnections1675940580449
33	1676996103000	MigrateExecutionStatus1676996103000
34	1677236854063	UpdateRunningExecutionStatus1677236854063
35	1677501636754	CreateVariables1677501636754
36	1679416281778	CreateExecutionMetadataTable1679416281778
37	1681134145996	AddUserActivatedProperty1681134145996
38	1681134145997	RemoveSkipOwnerSetup1681134145997
39	1690000000000	MigrateIntegerKeysToString1690000000000
40	1690000000020	SeparateExecutionData1690000000020
41	1690000000030	RemoveResetPasswordColumns1690000000030
42	1690000000030	AddMfaColumns1690000000030
43	1690787606731	AddMissingPrimaryKeyOnExecutionData1690787606731
44	1691088862123	CreateWorkflowNameIndex1691088862123
45	1692967111175	CreateWorkflowHistoryTable1692967111175
46	1693491613982	ExecutionSoftDelete1693491613982
47	1693554410387	DisallowOrphanExecutions1693554410387
48	1694091729095	MigrateToTimestampTz1694091729095
49	1695128658538	AddWorkflowMetadata1695128658538
50	1695829275184	ModifyWorkflowHistoryNodesAndConnections1695829275184
51	1700571993961	AddGlobalAdminRole1700571993961
52	1705429061930	DropRoleMapping1705429061930
53	1711018413374	RemoveFailedExecutionStatus1711018413374
54	1711390882123	MoveSshKeysToDatabase1711390882123
55	1712044305787	RemoveNodesAccess1712044305787
56	1714133768519	CreateProject1714133768519
57	1714133768521	MakeExecutionStatusNonNullable1714133768521
58	1717498465931	AddActivatedAtUserSetting1717498465931
59	1720101653148	AddConstraintToExecutionMetadata1720101653148
60	1721377157740	FixExecutionMetadataSequence1721377157740
61	1723627610222	CreateInvalidAuthTokenTable1723627610222
62	1723796243146	RefactorExecutionIndices1723796243146
63	1724753530828	CreateAnnotationTables1724753530828
64	1724951148974	AddApiKeysTable1724951148974
65	1726606152711	CreateProcessedDataTable1726606152711
66	1727427440136	SeparateExecutionCreationFromStart1727427440136
67	1728659839644	AddMissingPrimaryKeyOnAnnotationTagMapping1728659839644
68	1729607673464	UpdateProcessedDataValueColumnToText1729607673464
69	1729607673469	AddProjectIcons1729607673469
70	1730386903556	CreateTestDefinitionTable1730386903556
71	1731404028106	AddDescriptionToTestDefinition1731404028106
72	1731582748663	MigrateTestDefinitionKeyToString1731582748663
73	1732271325258	CreateTestMetricTable1732271325258
74	1732549866705	CreateTestRun1732549866705
75	1733133775640	AddMockedNodesColumnToTestDefinition1733133775640
76	1734479635324	AddManagedColumnToCredentialsTable1734479635324
77	1736172058779	AddStatsColumnsToTestRun1736172058779
78	1736947513045	CreateTestCaseExecutionTable1736947513045
79	1737715421462	AddErrorColumnsToTestRuns1737715421462
80	1738709609940	CreateFolderTable1738709609940
81	1739549398681	CreateAnalyticsTables1739549398681
82	1740445074052	UpdateParentFolderIdColumn1740445074052
83	1741167584277	RenameAnalyticsToInsights1741167584277
84	1742918400000	AddScopesColumnToApiKeys1742918400000
85	1745322634000	ClearEvaluation1745322634000
86	1745587087521	AddWorkflowStatisticsRootCount1745587087521
87	1745934666076	AddWorkflowArchivedColumn1745934666076
88	1745934666077	DropRoleTable1745934666077
89	1747824239000	AddProjectDescriptionColumn1747824239000
90	1750252139166	AddLastActiveAtColumnToUser1750252139166
91	1750252139166	AddScopeTables1750252139166
92	1750252139167	AddRolesTables1750252139167
93	1750252139168	LinkRoleToUserTable1750252139168
94	1750252139170	RemoveOldRoleColumn1750252139170
95	1752669793000	AddInputsOutputsToTestCaseExecution1752669793000
96	1753953244168	LinkRoleToProjectRelationTable1753953244168
97	1754475614601	CreateDataStoreTables1754475614601
98	1754475614602	ReplaceDataStoreTablesWithDataTables1754475614602
99	1756906557570	AddTimestampsToRoleAndRoleIndexes1756906557570
100	1758731786132	AddAudienceColumnToApiKeys1758731786132
101	1758794506893	AddProjectIdToVariableTable1758794506893
102	1759399811000	ChangeValueTypesForInsights1759399811000
\.


--
-- Data for Name: processed_data; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.processed_data ("workflowId", context, "createdAt", "updatedAt", value) FROM stdin;
\.


--
-- Data for Name: project; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.project (id, name, type, "createdAt", "updatedAt", icon, description) FROM stdin;
CwW1eE9ifm3lYFC9	Malachy Egbu <zubbyik@gmail.com>	personal	2025-10-23 21:25:40.771+00	2025-10-24 19:14:40.667+00	\N	\N
\.


--
-- Data for Name: project_relation; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.project_relation ("projectId", "userId", role, "createdAt", "updatedAt") FROM stdin;
CwW1eE9ifm3lYFC9	b217c4b8-96e3-47ad-b586-d71411066938	project:personalOwner	2025-10-23 21:25:40.771+00	2025-10-23 21:25:40.771+00
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.role (slug, "displayName", description, "roleType", "systemRole", "createdAt", "updatedAt") FROM stdin;
global:owner	Owner	Owner	global	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.664+00
global:admin	Admin	Admin	global	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.664+00
global:member	Member	Member	global	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.664+00
project:admin	Project Admin	Full control of settings, members, workflows, credentials and executions	project	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.711+00
project:personalOwner	Project Owner	Project Owner	project	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.711+00
project:editor	Project Editor	Create, edit, and delete workflows, credentials, and executions	project	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.711+00
project:viewer	Project Viewer	Read-only access to workflows, credentials, and executions	project	t	2025-10-23 21:25:42.39+00	2025-10-23 21:25:42.711+00
credential:owner	Credential Owner	Credential Owner	credential	t	2025-10-23 21:25:42.73+00	2025-10-23 21:25:42.73+00
credential:user	Credential User	Credential User	credential	t	2025-10-23 21:25:42.73+00	2025-10-23 21:25:42.73+00
workflow:owner	Workflow Owner	Workflow Owner	workflow	t	2025-10-23 21:25:42.735+00	2025-10-23 21:25:42.735+00
workflow:editor	Workflow Editor	Workflow Editor	workflow	t	2025-10-23 21:25:42.735+00	2025-10-23 21:25:42.735+00
\.


--
-- Data for Name: role_scope; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.role_scope ("roleSlug", "scopeSlug") FROM stdin;
global:owner	annotationTag:create
global:owner	annotationTag:read
global:owner	annotationTag:update
global:owner	annotationTag:delete
global:owner	annotationTag:list
global:owner	auditLogs:manage
global:owner	banner:dismiss
global:owner	community:register
global:owner	communityPackage:install
global:owner	communityPackage:uninstall
global:owner	communityPackage:update
global:owner	communityPackage:list
global:owner	credential:share
global:owner	credential:move
global:owner	credential:create
global:owner	credential:read
global:owner	credential:update
global:owner	credential:delete
global:owner	credential:list
global:owner	externalSecretsProvider:sync
global:owner	externalSecretsProvider:create
global:owner	externalSecretsProvider:read
global:owner	externalSecretsProvider:update
global:owner	externalSecretsProvider:delete
global:owner	externalSecretsProvider:list
global:owner	externalSecret:list
global:owner	externalSecret:use
global:owner	eventBusDestination:test
global:owner	eventBusDestination:create
global:owner	eventBusDestination:read
global:owner	eventBusDestination:update
global:owner	eventBusDestination:delete
global:owner	eventBusDestination:list
global:owner	ldap:sync
global:owner	ldap:manage
global:owner	license:manage
global:owner	logStreaming:manage
global:owner	orchestration:read
global:owner	project:create
global:owner	project:read
global:owner	project:update
global:owner	project:delete
global:owner	project:list
global:owner	saml:manage
global:owner	securityAudit:generate
global:owner	sourceControl:pull
global:owner	sourceControl:push
global:owner	sourceControl:manage
global:owner	tag:create
global:owner	tag:read
global:owner	tag:update
global:owner	tag:delete
global:owner	tag:list
global:owner	user:resetPassword
global:owner	user:changeRole
global:owner	user:enforceMfa
global:owner	user:create
global:owner	user:read
global:owner	user:update
global:owner	user:delete
global:owner	user:list
global:owner	variable:create
global:owner	variable:read
global:owner	variable:update
global:owner	variable:delete
global:owner	variable:list
global:owner	projectVariable:create
global:owner	projectVariable:read
global:owner	projectVariable:update
global:owner	projectVariable:delete
global:owner	projectVariable:list
global:owner	workersView:manage
global:owner	workflow:share
global:owner	workflow:execute
global:owner	workflow:move
global:owner	workflow:create
global:owner	workflow:read
global:owner	workflow:update
global:owner	workflow:delete
global:owner	workflow:list
global:owner	folder:create
global:owner	folder:read
global:owner	folder:update
global:owner	folder:delete
global:owner	folder:list
global:owner	folder:move
global:owner	insights:list
global:owner	oidc:manage
global:owner	dataTable:list
global:owner	role:manage
global:owner	mcp:manage
global:owner	mcpApiKey:create
global:owner	mcpApiKey:rotate
global:owner	chatHub:manage
global:owner	chatHub:message
global:admin	annotationTag:create
global:admin	annotationTag:read
global:admin	annotationTag:update
global:admin	annotationTag:delete
global:admin	annotationTag:list
global:admin	auditLogs:manage
global:admin	banner:dismiss
global:admin	community:register
global:admin	communityPackage:install
global:admin	communityPackage:uninstall
global:admin	communityPackage:update
global:admin	communityPackage:list
global:admin	credential:share
global:admin	credential:move
global:admin	credential:create
global:admin	credential:read
global:admin	credential:update
global:admin	credential:delete
global:admin	credential:list
global:admin	externalSecretsProvider:sync
global:admin	externalSecretsProvider:create
global:admin	externalSecretsProvider:read
global:admin	externalSecretsProvider:update
global:admin	externalSecretsProvider:delete
global:admin	externalSecretsProvider:list
global:admin	externalSecret:list
global:admin	externalSecret:use
global:admin	eventBusDestination:test
global:admin	eventBusDestination:create
global:admin	eventBusDestination:read
global:admin	eventBusDestination:update
global:admin	eventBusDestination:delete
global:admin	eventBusDestination:list
global:admin	ldap:sync
global:admin	ldap:manage
global:admin	license:manage
global:admin	logStreaming:manage
global:admin	orchestration:read
global:admin	project:create
global:admin	project:read
global:admin	project:update
global:admin	project:delete
global:admin	project:list
global:admin	saml:manage
global:admin	securityAudit:generate
global:admin	sourceControl:pull
global:admin	sourceControl:push
global:admin	sourceControl:manage
global:admin	tag:create
global:admin	tag:read
global:admin	tag:update
global:admin	tag:delete
global:admin	tag:list
global:admin	user:resetPassword
global:admin	user:changeRole
global:admin	user:enforceMfa
global:admin	user:create
global:admin	user:read
global:admin	user:update
global:admin	user:delete
global:admin	user:list
global:admin	variable:create
global:admin	variable:read
global:admin	variable:update
global:admin	variable:delete
global:admin	variable:list
global:admin	projectVariable:create
global:admin	projectVariable:read
global:admin	projectVariable:update
global:admin	projectVariable:delete
global:admin	projectVariable:list
global:admin	workersView:manage
global:admin	workflow:share
global:admin	workflow:execute
global:admin	workflow:move
global:admin	workflow:create
global:admin	workflow:read
global:admin	workflow:update
global:admin	workflow:delete
global:admin	workflow:list
global:admin	folder:create
global:admin	folder:read
global:admin	folder:update
global:admin	folder:delete
global:admin	folder:list
global:admin	folder:move
global:admin	insights:list
global:admin	oidc:manage
global:admin	dataTable:list
global:admin	role:manage
global:admin	mcp:manage
global:admin	mcpApiKey:create
global:admin	mcpApiKey:rotate
global:admin	chatHub:manage
global:admin	chatHub:message
global:member	annotationTag:create
global:member	annotationTag:read
global:member	annotationTag:update
global:member	annotationTag:delete
global:member	annotationTag:list
global:member	eventBusDestination:test
global:member	eventBusDestination:list
global:member	tag:create
global:member	tag:read
global:member	tag:update
global:member	tag:list
global:member	user:list
global:member	variable:read
global:member	variable:list
global:member	dataTable:list
global:member	mcpApiKey:create
global:member	mcpApiKey:rotate
global:member	chatHub:message
project:admin	credential:share
project:admin	credential:move
project:admin	credential:create
project:admin	credential:read
project:admin	credential:update
project:admin	credential:delete
project:admin	credential:list
project:admin	project:read
project:admin	project:update
project:admin	project:delete
project:admin	project:list
project:admin	sourceControl:push
project:admin	projectVariable:create
project:admin	projectVariable:read
project:admin	projectVariable:update
project:admin	projectVariable:delete
project:admin	projectVariable:list
project:admin	workflow:execute
project:admin	workflow:move
project:admin	workflow:create
project:admin	workflow:read
project:admin	workflow:update
project:admin	workflow:delete
project:admin	workflow:list
project:admin	folder:create
project:admin	folder:read
project:admin	folder:update
project:admin	folder:delete
project:admin	folder:list
project:admin	folder:move
project:admin	dataTable:create
project:admin	dataTable:read
project:admin	dataTable:update
project:admin	dataTable:delete
project:admin	dataTable:readRow
project:admin	dataTable:writeRow
project:admin	dataTable:listProject
project:personalOwner	credential:share
project:personalOwner	credential:move
project:personalOwner	credential:create
project:personalOwner	credential:read
project:personalOwner	credential:update
project:personalOwner	credential:delete
project:personalOwner	credential:list
project:personalOwner	project:read
project:personalOwner	project:list
project:personalOwner	workflow:share
project:personalOwner	workflow:execute
project:personalOwner	workflow:move
project:personalOwner	workflow:create
project:personalOwner	workflow:read
project:personalOwner	workflow:update
project:personalOwner	workflow:delete
project:personalOwner	workflow:list
project:personalOwner	folder:create
project:personalOwner	folder:read
project:personalOwner	folder:update
project:personalOwner	folder:delete
project:personalOwner	folder:list
project:personalOwner	folder:move
project:personalOwner	dataTable:create
project:personalOwner	dataTable:read
project:personalOwner	dataTable:update
project:personalOwner	dataTable:delete
project:personalOwner	dataTable:readRow
project:personalOwner	dataTable:writeRow
project:personalOwner	dataTable:listProject
project:editor	credential:create
project:editor	credential:read
project:editor	credential:update
project:editor	credential:delete
project:editor	credential:list
project:editor	project:read
project:editor	project:list
project:editor	projectVariable:create
project:editor	projectVariable:read
project:editor	projectVariable:update
project:editor	projectVariable:delete
project:editor	projectVariable:list
project:editor	workflow:execute
project:editor	workflow:create
project:editor	workflow:read
project:editor	workflow:update
project:editor	workflow:delete
project:editor	workflow:list
project:editor	folder:create
project:editor	folder:read
project:editor	folder:update
project:editor	folder:delete
project:editor	folder:list
project:editor	dataTable:create
project:editor	dataTable:read
project:editor	dataTable:update
project:editor	dataTable:delete
project:editor	dataTable:readRow
project:editor	dataTable:writeRow
project:editor	dataTable:listProject
project:viewer	credential:read
project:viewer	credential:list
project:viewer	project:read
project:viewer	project:list
project:viewer	projectVariable:read
project:viewer	projectVariable:list
project:viewer	workflow:read
project:viewer	workflow:list
project:viewer	folder:read
project:viewer	folder:list
project:viewer	dataTable:read
project:viewer	dataTable:readRow
project:viewer	dataTable:listProject
credential:owner	credential:share
credential:owner	credential:move
credential:owner	credential:read
credential:owner	credential:update
credential:owner	credential:delete
credential:user	credential:read
workflow:owner	workflow:share
workflow:owner	workflow:execute
workflow:owner	workflow:move
workflow:owner	workflow:read
workflow:owner	workflow:update
workflow:owner	workflow:delete
workflow:editor	workflow:execute
workflow:editor	workflow:read
workflow:editor	workflow:update
\.


--
-- Data for Name: scope; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.scope (slug, "displayName", description) FROM stdin;
annotationTag:create	Create Annotation Tag	Allows creating new annotation tags.
annotationTag:read	annotationTag:read	\N
annotationTag:update	annotationTag:update	\N
annotationTag:delete	annotationTag:delete	\N
annotationTag:list	annotationTag:list	\N
annotationTag:*	annotationTag:*	\N
auditLogs:manage	auditLogs:manage	\N
auditLogs:*	auditLogs:*	\N
banner:dismiss	banner:dismiss	\N
banner:*	banner:*	\N
community:register	community:register	\N
community:*	community:*	\N
communityPackage:install	communityPackage:install	\N
communityPackage:uninstall	communityPackage:uninstall	\N
communityPackage:update	communityPackage:update	\N
communityPackage:list	communityPackage:list	\N
communityPackage:manage	communityPackage:manage	\N
communityPackage:*	communityPackage:*	\N
credential:share	credential:share	\N
credential:move	credential:move	\N
credential:create	credential:create	\N
credential:read	credential:read	\N
credential:update	credential:update	\N
credential:delete	credential:delete	\N
credential:list	credential:list	\N
credential:*	credential:*	\N
externalSecretsProvider:sync	externalSecretsProvider:sync	\N
externalSecretsProvider:create	externalSecretsProvider:create	\N
externalSecretsProvider:read	externalSecretsProvider:read	\N
externalSecretsProvider:update	externalSecretsProvider:update	\N
externalSecretsProvider:delete	externalSecretsProvider:delete	\N
externalSecretsProvider:list	externalSecretsProvider:list	\N
externalSecretsProvider:*	externalSecretsProvider:*	\N
externalSecret:list	externalSecret:list	\N
externalSecret:use	externalSecret:use	\N
externalSecret:*	externalSecret:*	\N
eventBusDestination:test	eventBusDestination:test	\N
eventBusDestination:create	eventBusDestination:create	\N
eventBusDestination:read	eventBusDestination:read	\N
eventBusDestination:update	eventBusDestination:update	\N
eventBusDestination:delete	eventBusDestination:delete	\N
eventBusDestination:list	eventBusDestination:list	\N
eventBusDestination:*	eventBusDestination:*	\N
ldap:sync	ldap:sync	\N
ldap:manage	ldap:manage	\N
ldap:*	ldap:*	\N
license:manage	license:manage	\N
license:*	license:*	\N
logStreaming:manage	logStreaming:manage	\N
logStreaming:*	logStreaming:*	\N
orchestration:read	orchestration:read	\N
orchestration:list	orchestration:list	\N
orchestration:*	orchestration:*	\N
project:create	project:create	\N
project:read	project:read	\N
project:update	project:update	\N
project:delete	project:delete	\N
project:list	project:list	\N
project:*	project:*	\N
saml:manage	saml:manage	\N
saml:*	saml:*	\N
securityAudit:generate	securityAudit:generate	\N
securityAudit:*	securityAudit:*	\N
sourceControl:pull	sourceControl:pull	\N
sourceControl:push	sourceControl:push	\N
sourceControl:manage	sourceControl:manage	\N
sourceControl:*	sourceControl:*	\N
tag:create	tag:create	\N
tag:read	tag:read	\N
tag:update	tag:update	\N
tag:delete	tag:delete	\N
tag:list	tag:list	\N
tag:*	tag:*	\N
user:resetPassword	user:resetPassword	\N
user:changeRole	user:changeRole	\N
user:enforceMfa	user:enforceMfa	\N
user:create	user:create	\N
user:read	user:read	\N
user:update	user:update	\N
user:delete	user:delete	\N
user:list	user:list	\N
user:*	user:*	\N
variable:create	variable:create	\N
variable:read	variable:read	\N
variable:update	variable:update	\N
variable:delete	variable:delete	\N
variable:list	variable:list	\N
variable:*	variable:*	\N
projectVariable:create	projectVariable:create	\N
projectVariable:read	projectVariable:read	\N
projectVariable:update	projectVariable:update	\N
projectVariable:delete	projectVariable:delete	\N
projectVariable:list	projectVariable:list	\N
projectVariable:*	projectVariable:*	\N
workersView:manage	workersView:manage	\N
workersView:*	workersView:*	\N
workflow:share	workflow:share	\N
workflow:execute	workflow:execute	\N
workflow:move	workflow:move	\N
workflow:activate	workflow:activate	\N
workflow:deactivate	workflow:deactivate	\N
workflow:create	workflow:create	\N
workflow:read	workflow:read	\N
workflow:update	workflow:update	\N
workflow:delete	workflow:delete	\N
workflow:list	workflow:list	\N
workflow:*	workflow:*	\N
folder:create	folder:create	\N
folder:read	folder:read	\N
folder:update	folder:update	\N
folder:delete	folder:delete	\N
folder:list	folder:list	\N
folder:move	folder:move	\N
folder:*	folder:*	\N
insights:list	insights:list	\N
insights:*	insights:*	\N
oidc:manage	oidc:manage	\N
oidc:*	oidc:*	\N
dataTable:create	dataTable:create	\N
dataTable:read	dataTable:read	\N
dataTable:update	dataTable:update	\N
dataTable:delete	dataTable:delete	\N
dataTable:list	dataTable:list	\N
dataTable:readRow	dataTable:readRow	\N
dataTable:writeRow	dataTable:writeRow	\N
dataTable:listProject	dataTable:listProject	\N
dataTable:*	dataTable:*	\N
execution:delete	execution:delete	\N
execution:read	execution:read	\N
execution:retry	execution:retry	\N
execution:list	execution:list	\N
execution:get	execution:get	\N
execution:*	execution:*	\N
workflowTags:update	workflowTags:update	\N
workflowTags:list	workflowTags:list	\N
workflowTags:*	workflowTags:*	\N
role:manage	role:manage	\N
role:*	role:*	\N
mcp:manage	mcp:manage	\N
mcp:*	mcp:*	\N
mcpApiKey:create	mcpApiKey:create	\N
mcpApiKey:rotate	mcpApiKey:rotate	\N
mcpApiKey:*	mcpApiKey:*	\N
chatHub:manage	chatHub:manage	\N
chatHub:message	chatHub:message	\N
chatHub:*	chatHub:*	\N
*	*	\N
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.settings (key, value, "loadOnStartup") FROM stdin;
ui.banners.dismissed	["V1"]	t
features.ldap	{"loginEnabled":false,"loginLabel":"","connectionUrl":"","allowUnauthorizedCerts":false,"connectionSecurity":"none","connectionPort":389,"baseDn":"","bindingAdminDn":"","bindingAdminPassword":"","firstNameAttribute":"","lastNameAttribute":"","emailAttribute":"","loginIdAttribute":"","ldapIdAttribute":"","userFilter":"","synchronizationEnabled":false,"synchronizationInterval":60,"searchPageSize":0,"searchTimeout":60}	t
userManagement.authenticationMethod	email	t
features.sourceControl.sshKeys	{"encryptedPrivateKey":"U2FsdGVkX19NEfzHYNv4DpKy41QXqRwZZBJzzVhvB7dbAoeVPdLCV8qG7PWSTjnbR/DrMYh2xpdRwE42vYjMJnvbN5iF9qpBSjr6Rq/BDtpd5U86qLwEJacZPvyTyNyn+D6kM+/zw9neQq212Rk+oOzh2FN3/v1atp8igE4/LX5X8AcVmAcxy0CsHb4uZ1EXks4NM0cWjSxiuavO9s8TuVwQ6l0I0AOzMdbKdpkZ2+lzVduN72+jNKuGZPp0cU2EUXaHnn70qAZ5lyykFg2a0plpXjBcz/jWsTW25x/kJbyFOg2KFrG0OucPLda0bHglXPbZDF4lSdpl5rAszs5QHQrLWfNidvwbiCj3C+JbDF/xH1C0LYAudsVXBlcrAxYrUgffrzPFC58wAYcNN/4115C3Ki3xDJ53ZmT7Vnw3D0Zk9h13gGYAR0POI6M4MPaOgXJiswvo6W4pHbzXgZlCXAre+A0s5nh1jvwULRaFgvG7w3HtPMJg4HqJszCK2/Xh5sDC2JotI5848fEKhZ1yj3slogMzBN2i29jIlRP3gyTbNQRkuihnIop3uNECz3wv","publicKey":"ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAHzYNy81U8FdJCpHwCn1psetvf3WKPPgKLJlj6yr/o/ n8n deploy key"}	t
features.sourceControl	{"branchName":"main","connectionType":"ssh","keyGeneratorType":"ed25519"}	t
userManagement.isInstanceOwnerSetUp	true	t
license.cert	eyJsaWNlbnNlS2V5IjoiLS0tLS1CRUdJTiBMSUNFTlNFIEtFWS0tLS0tXG5XOXVTVloyVVNPTCtFRnRuRnlTT1dDODlDdzR6Vm5NbGVxOHpLbVpXQ3R0S2VOaVFvS0s2b2c1dVhuNkZHTmR0XG5ZVkFjY3hIcjVhTzFvck0wdlJlbHdPd21KS2wrZXQyeTNpUnN6alBnc3NCcjRXU2R0dFZXTXV1a2Qyb25EaGxOXG5zalZJTkhyelZ3aCtTMHgyejNjSGpETkZmMFVFVFhNYnorakVMQllMWGhBMDhyQVR4V2VSSCsyY0pMMFBjeTlBXG5ZL1UxQjBCbUFkUFJMMmxmR1MvNHhkV3JuMEQwVTh4ZDBuNExMTmdRMDFmeGNFZ0dLZHloN2RlRnE0KzVhbXFuXG5EM0tCalBEcW9jTUFwOUdSOVdWSVZqcVhBc3dQZUZEeHFPNm4rWnFoeTZjdzJLbFJKYU9iOEo1cEN4S21wTXpSXG5hV1BTVDNSRnpJNzZvT0QrdkVDNVZnPT18fFUyRnNkR1ZrWDEvMzFEWmRpTGh5S2MwWTBHY0ttbEFWeDdFamtGXG4xVTJRZWs4Ykc5Ly9HclAyeW45NkF5VmhZYlJadnZaWGdPQWpIUzk1TFowaERidE8vb0IvQW9sUWI1ejhRU2VBXG5oMkx0cmV3OTFBbEhXeWhTTTNqcmZjbVpjRXRwVDB1anVBQ2llcW4raSt2U1BoNzFJQ0ZydnVEMHcvSnVCRkZ0XG5zSFloU1Q5dFhKZzRnK0RVMzlSbXVhaFJoOHRIcnRwSDk3bjBGdWs5NDhJWWc4T2hhZjJWKzM0VXpZbGpsMk1tXG5qK3JLbXNuMUVwb2hHeW9hVUZLVWpIWHNBL2psaWI1VzdLeEhXdStJQVloL05pZHNKdDBUb3Q2ZmtldGVmZkdvXG5lOXJ4aUNTbGlxQkxrdlcxSkJJdnA2eVpXViszamlIbU4zd0NKQ3RLNHFzdTR6SmxBUUxsTlovMW5LdWhtSWZGXG5DRmt1U2E2aUJmUWVoZlhHZGFwUnE1cENWWm5EaXlBcnZtTmcybUc4YllPa2NIUVBwTDBwaGJIRTdwMzVZUHVUXG5mNzJMZUtCVEVDOWVvcmFxSG5xbTF6TnZnVTRWRGY4NUZHeVhmMzFkTVVKZnZrQzhGWDVlT2NoWkR5RWNJajJFXG4ybWt1WjVYeER1STdRMnoxUmJpUjBLUlZxTFNsa096S3ptVzVrM0ZXcUMwOGoyR25waU5NZUJxdm1HUzQ5K1FGXG5YK09xSXp4aDRqRWlsWEplU3pENHlXOTN3b2ZYSkhFYmxiVjh3OU4yUWtXNG1ycWFpM3dBVU1Yei92VFQ3dkxZXG5McnZTQkxlbm5rWGhQR0pRUktadCswM0dzbzJ2NlJ3V0l0dElQSWswbUJMdEw1c04rNlNiYjZrSSt1VDBGUWM4XG5aRlRYSkUxS1JzSHVRSEJTN2pRKzZCNFZ1RU5Ud3FUSkN0L01UUEtkMzk1MnozNmREYUxVOFpUT05Bd3hkcExzXG5MS2phTStiK2FYaDZzemJkdks4Q2pxRURqUXJZN0l2VDJYQkVoa2sxdjM3d0k1dTZJNnA2R3FZNkNsRzNoVnNBXG51OFRHYzlsQktxaGozYURwTjR0WFFKZlF1b0VrQ2ZMTUUrMUNtN2x4T0trdElmWVVWQmVmK2VsYmVGM2FJZGplXG5VVkpVMGNoZlo2c3U0R21GZ0NYVXMwMzZ6aFEzekowSEVDdzJRdWI0MDJHa2tkZnBQSzY5SkZ1VWlscjI2WG55XG5zWXZLdStpK3hiTHoyME8yaCtYMjlXOFhvWk5ETU1iUWp0NEdWNXFzNzVoVVV6dmRIYTNqbkl4MjJ6V3QyNzRhXG5PZTU3UWNHSlRNK0pFck5nQzJMTW1YaHBwblJReWhMV1ZpVmZyMTN4NUp6TEZtMm5mKzZnOGFNOHF0cWFMRmF2XG5SbnRVWUhqNXJxNGNSKzRSYU9yNURRMVdISkt5ZnBReGNQSzFGZW1QblNaSjNDRUxQcTA5SWhWSmtFMWNCTjVjXG5SWksxRGltSW41aU1yU1UwUkw3d1dSUW9iRmNlelNZNVp3c3N0amxJaTBWaW5HWVNvMXBkQTFHL0xZTmgzdnVWXG5vcXNLRm14ZmdHWDc5RkJUSHRVSUovQWtBbVBPTmVvTVMzc1RmNHF1YVpJR0RmTXA3dUhOc3N4Yk5xRTZ1NERTXG5ZdnBKNjJBc3Bmc1oxT1c1VDZaRnI1d0RGMWJqMEcwK2FtUjN2MCs4MjhnQmovejF2UG5nMHZNbW9LS01aTWlXXG5BbExwOWtzYVVzZGRXQ1lQT280RFE4elBuT3hvWm1PUnpyc2JEeEdFWVpMczQ0RHdvTWpRN0NtUmpkb0lFL283XG45UWpTcnk3VHBQZGluY0E3em9YaDkzN1FvZnZ5MVpvT2t3dGluVnlTcFYrMFVyVllIeE5BWjVKVWhPOERZNU9IXG5XaVl1dEtZS0g2elVuTTUvRUx2aU4zVm1pOVVxWWEyaHVETHNrK3czZk42bDFzZFB3ZEwzYmxKbXlxUGNWUWVyXG5zZkdoaTRnUnhTTTZFOW9lWEtpQ0lIK3E5WGF0QW5wemc5eXh3bDRhdFRrcGdMb2YySGV2cVVvUVQ4Qk13dDU1XG40TzdyeGhPdmt5aWIzRXIrdHl1V3dXL3RrVytzcGo3WGhJWFlianFraFlTQS8vSVpKY2VNV2R3ekY0WUwySG9hXG54eGs1TU13YjhqWHNVTnlBUTFKMGlhTkhudGN3eThXVTVYdDRVSjRmNFZLeUFvTU4vTmNIL0hxdU10YXMrVHVhXG5hNzFTNEwzczgxNGx0QlU3NGt1aytIQXJQTkpsV0tpc2xWUzNIbnNTbHBUc21uV285RER5eEhRTk1RbTVRb2JVXG4yZGFrU2Z1S2ZIc0VPOFVEZGJ0OS9IMytwazlORWM1RFpPS0RkWFdiR3VOZmVzSXBmQXI2SityaGZRYTdJd1lPXG5ZbVNZNzVmL0lidlREY21PbHZudFhIaEpDSGJMNWdLUGJyT1NCN2FzVm9nWGFzdUxQbWUzRlBWaGszaVVBem0zXG5yYUlSVmFJMU5pZjRscXVrak5JQ3QvR2VlSjhwbll5cFVHODIxQkNMMkEveVBLQUFRTThJc0hHeEJSL1FsMlZ0XG5aaUlsUGhwbTlLYzdpN21KZHBTWnlIUFNWU1RucE1sQjNCT29DUWtWak1CNzdlQWVJSFQzc2cycTBNT3ZPM3B2XG5Ec1pVdytVMzFia3hjS2FvVWN4akNZZ1NpOEhMelNSdVJ5MTBCNHE2RUcvcFBHV2xEUmQvWE9kZG9GWCs5WE1uXG4zbmJTcGxsVzFUQy9Oc2dTbnFXMkQ3ZmNHUXhaN1ZyVC9Nc2tjZ21OTERrUWx2SFZUR2pOamxmbnhkYlVSeTBaXG5RK1N6QThBYXA4UHNicFloTVMvc1hHeXI0YWptdGpZUGNBRWVPSnY0RVZ3eFM5czR6MEZIc2N2NXhRUWcyVW41XG4wNGEyUHNMeFViRkVuUVhjSklrVFNYRnJkWnhGYlRJNFMrd0JSV3FFM1FqRHRTNHlta09qbU43M0ZTQ1V4OFZIXG5ab091dGNFbVd1YjVHdlhPWVAxMkhFN24yRzVJN1BtaDdYNlMzckY3b1I2UzZDeVE9PXx8bFcrRnAzRjg3L0hLXG56UnJlQzJ3R21UdFFhSDhWbGViTVFkYXZRQ2pLak9QdXB3UnNaQ3pQekVibWlQNTI2VXUyOFJLcWl3Vk5Gd2lxXG5VWHNMdVVjcWpkTkg1MmV0MXEzblFIZlgxV1JZSGxZQytOQ0g4eklPek5zcGIweHQ1UlQ0V3VPTTAxRnBYT0tDXG55YVdONzVlci9TbFgvTFlYSENJbGFxZmhwbTN6WWMrOEFQRGhhRVpZU0hjb0ZnSEtIYXh0b0hHWXVtdmJEU0lTXG5xV0kyY3RNVVR0OUVHZ3FyU1crcXBjUWlwdGl1QUVrY0lTOEwrVDdEaWF5VDF6VXIxU3F1b1o5MENPSUVQUXRSXG43cFJNajZhZ3NoZWNwa0NyRElnY2NPOXY1SE5mbS9nd0NTT1crVGhGT21meDVZTCtCbDJad2I3a3RJN05EakwvXG51Lzl3UTNONnlnPT1cbi0tLS0tRU5EIExJQ0VOU0UgS0VZLS0tLS0iLCJ4NTA5IjoiLS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tXG5NSUlFRERDQ0FmUUNDUUNxZzJvRFQ4MHh3akFOQmdrcWhraUc5dzBCQVFVRkFEQklNUXN3Q1FZRFZRUUdFd0pFXG5SVEVQTUEwR0ExVUVDQXdHUW1WeWJHbHVNUTh3RFFZRFZRUUhEQVpDWlhKc2FXNHhGekFWQmdOVkJBTU1EbXhwXG5ZMlZ1YzJVdWJqaHVMbWx2TUI0WERUSXlNRFl5TkRBME1UQTBNRm9YRFRJek1EWXlOREEwTVRBME1Gb3dTREVMXG5NQWtHQTFVRUJoTUNSRVV4RHpBTkJnTlZCQWdNQmtKbGNteHBiakVQTUEwR0ExVUVCd3dHUW1WeWJHbHVNUmN3XG5GUVlEVlFRRERBNXNhV05sYm5ObExtNDRiaTVwYnpDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDXG5BUW9DZ2dFQkFNQk0wNVhCNDRnNXhmbUNMd2RwVVR3QVQ4K0NCa3lMS0ZzZXprRDVLLzZXaGFYL1hyc2QvUWQwXG4yMEo3d2w1V2RIVTRjVkJtRlJqVndWemtsQ0syeVlKaThtang4c1hzR3E5UTFsYlVlTUtmVjlkc2dmdWhubEFTXG50blFaZ2x1Z09uRjJGZ1JoWGIvakswdHhUb2FvK2JORTZyNGdJRXpwa3RITEJUWXZ2aXVKbXJlZjdXYlBSdDRJXG5uZDlEN2xoeWJlYnloVjdrdXpqUUEvcFBLSFRGczhNVEhaOGhZVXhSeXJwbTMrTVl6UUQrYmpBMlUxRkljdGFVXG53UVhZV2FON3QydVR3Q3Q5ekFLc21ZL1dlT2J2bDNUWk41T05MQXp5V0dDdWxtNWN3S1IzeGJsQlp6WG5CNmdzXG5Pbk4yT0FkU3RjelRWQ3ljbThwY0ZVcnl0S1NLa0dFQ0F3RUFBVEFOQmdrcWhraUc5dzBCQVFVRkFBT0NBZ0VBXG5sSjAxd2NuMXZqWFhDSHVvaTdSMERKMWxseDErZGFmcXlFcVBBMjdKdStMWG1WVkdYUW9yUzFiOHhqVXFVa2NaXG5UQndiV0ZPNXo1ZFptTnZuYnlqYXptKzZvT2cwUE1hWXhoNlRGd3NJMlBPYmM3YkZ2MmVheXdQdC8xQ3BuYzQwXG5xVU1oZnZSeC9HQ1pQQ1d6My8yUlBKV1g5alFEU0hYQ1hxOEJXK0kvM2N1TERaeVkzZkVZQkIwcDNEdlZtYWQ2XG42V0hRYVVyaU4wL0xxeVNPcC9MWmdsbC90MDI5Z1dWdDA1WmliR29LK2NWaFpFY3NMY1VJaHJqMnVGR0ZkM0ltXG5KTGcxSktKN2pLU0JVUU9kSU1EdnNGVUY3WWRNdk11ckNZQTJzT05OOENaK0k1eFFWMUtTOWV2R0hNNWZtd2dTXG5PUEZ2UHp0RENpMC8xdVc5dE9nSHBvcnVvZGFjdCtFWk5rQVRYQ3ZaaXUydy9xdEtSSkY0VTRJVEVtNWFXMGt3XG42enVDOHh5SWt0N3ZoZHM0OFV1UlNHSDlqSnJBZW1sRWl6dEdJTGhHRHF6UUdZYmxoVVFGR01iQmI3amhlTHlDXG5MSjFXT0c2MkYxc3B4Q0tCekVXNXg2cFIxelQxbWhFZ2Q0TWtMYTZ6UFRwYWNyZDk1QWd4YUdLRUxhMVJXU0ZwXG5NdmRoR2s0TnY3aG5iOHIrQnVNUkM2aWVkUE1DelhxL001MGNOOEFnOGJ3K0oxYUZvKzBFSzJoV0phN2tpRStzXG45R3ZGalNkekNGbFVQaEtra1Vaa1NvNWFPdGNRcTdKdTZrV0JoTG9GWUtncHJscDFRVkIwc0daQTZvNkR0cWphXG5HNy9SazZ2YmFZOHdzTllLMnpCWFRUOG5laDVab1JaL1BKTFV0RUV0YzdZPVxuLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLSJ9	f
\.


--
-- Data for Name: shared_credentials; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.shared_credentials ("credentialsId", "projectId", role, "createdAt", "updatedAt") FROM stdin;
7TdeyWV7he2JL6fk	CwW1eE9ifm3lYFC9	credential:owner	2025-10-29 21:27:28.454+00	2025-10-29 21:27:28.454+00
YGaPHefyc9NONFfU	CwW1eE9ifm3lYFC9	credential:owner	2025-11-08 17:47:04.233+00	2025-11-08 17:47:04.233+00
\.


--
-- Data for Name: shared_workflow; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.shared_workflow ("workflowId", "projectId", role, "createdAt", "updatedAt") FROM stdin;
wXJ6yePE9hpJPTta	CwW1eE9ifm3lYFC9	workflow:owner	2025-10-29 21:42:24.842+00	2025-10-29 21:42:24.842+00
\.


--
-- Data for Name: tag_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.tag_entity (name, "createdAt", "updatedAt", id) FROM stdin;
\.


--
-- Data for Name: test_case_execution; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.test_case_execution (id, "testRunId", "executionId", status, "runAt", "completedAt", "errorCode", "errorDetails", metrics, "createdAt", "updatedAt", inputs, outputs) FROM stdin;
\.


--
-- Data for Name: test_run; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.test_run (id, "workflowId", status, "errorCode", "errorDetails", "runAt", "completedAt", metrics, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public."user" (id, email, "firstName", "lastName", password, "personalizationAnswers", "createdAt", "updatedAt", settings, disabled, "mfaEnabled", "mfaSecret", "mfaRecoveryCodes", "lastActiveAt", "roleSlug") FROM stdin;
b217c4b8-96e3-47ad-b586-d71411066938	zubbyik@gmail.com	Malachy	Egbu	$2a$10$J38lYnDLedmD.hwxuiIAgOR6z8MVVYvkjc8LZrb1GXnFzBW1nAZ0y	{"version":"v4","personalization_survey_submitted_at":"2025-10-24T19:16:04.434Z","personalization_survey_n8n_version":"1.116.2","automationGoalDevops":["ticketing-systems-integrations","ci-cd","cloud-infrastructure-orchestration","monitoring-alerting"],"companyIndustryExtended":["it-industry","real-estate-or-construction"],"companySize":"personalUser","companyType":"other","role":"devops","reportedSource":"twitter"}	2025-10-23 21:25:39.434+00	2025-12-13 00:42:48.015+00	{"userActivated": false}	f	f	\N	\N	2025-12-12	global:owner
\.


--
-- Data for Name: user_api_keys; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.user_api_keys (id, "userId", label, "apiKey", "createdAt", "updatedAt", scopes, audience) FROM stdin;
\.


--
-- Data for Name: variables; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.variables (key, type, value, id, "projectId") FROM stdin;
\.


--
-- Data for Name: webhook_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.webhook_entity ("webhookPath", method, node, "webhookId", "pathLength", "workflowId") FROM stdin;
\.


--
-- Data for Name: workflow_entity; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.workflow_entity (name, active, nodes, connections, "createdAt", "updatedAt", settings, "staticData", "pinData", "versionId", "triggerCount", id, meta, "parentFolderId", "isArchived") FROM stdin;
My workflow	f	[{"parameters":{},"type":"n8n-nodes-base.manualTrigger","typeVersion":1,"position":[0,0],"id":"088f4146-9c93-4e20-8e37-e849e1ca5b4e","name":"When clicking ‘Execute workflow’"},{"parameters":{"url":"https://weatherbit-v1-mashape.p.rapidapi.com/forecast/3hourly?lat=35.5&lon=-78.5&units=imperial&lang=en","sendHeaders":true,"headerParameters":{"parameters":[{"name":"x-rapidapi-host","value":"weatherbit-v1-mashape.p.rapidapi.com"},{"name":"x-rapidapi-key","value":"kWlqHqDoPlmshSBhwnPRMfrjNVVjp1K0fOnjsnJiMXZxmTOU6W"}]},"options":{}},"type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[208,0],"id":"e2e1e067-53e8-46dc-aa7f-c1dbbbdb5b09","name":"HTTP Request"},{"parameters":{"fieldToSplitOut":"data","options":{}},"type":"n8n-nodes-base.splitOut","typeVersion":1,"position":[416,0],"id":"c51fc711-1737-490e-b5e4-5bdf32dbfd0a","name":"Split Out"},{"parameters":{"documentId":{"__rl":true,"value":"1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc","mode":"list","cachedResultName":"Weather Reported","cachedResultUrl":"https://docs.google.com/spreadsheets/d/1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc/edit?usp=drivesdk"},"sheetName":{"__rl":true,"value":"gid=0","mode":"list","cachedResultName":"Sheet1","cachedResultUrl":"https://docs.google.com/spreadsheets/d/1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc/edit#gid=0"},"options":{}},"type":"n8n-nodes-base.googleSheets","typeVersion":4.7,"position":[144,144],"id":"c2be632d-ab5a-4e08-a2b6-5ecc281c850f","name":"Get row(s) in sheet","credentials":{"googleSheetsOAuth2Api":{"id":"YGaPHefyc9NONFfU","name":"Google Sheets account"}}},{"parameters":{"operation":"update","documentId":{"__rl":true,"value":"1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc","mode":"list","cachedResultName":"Weather Reported","cachedResultUrl":"https://docs.google.com/spreadsheets/d/1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc/edit?usp=drivesdk"},"sheetName":{"__rl":true,"value":"gid=0","mode":"list","cachedResultName":"Sheet1","cachedResultUrl":"https://docs.google.com/spreadsheets/d/1awj5JC4DcnVlctz4w7X8npuP7PD7seCrK9mkCBJzpWc/edit#gid=0"},"columns":{"mappingMode":"defineBelow","value":{},"matchingColumns":[],"schema":[{"id":"Temperature","displayName":"Temperature","required":false,"defaultMatch":false,"display":true,"type":"string","canBeUsedToMatch":true},{"id":"cloud","displayName":"cloud","required":false,"defaultMatch":false,"display":true,"type":"string","canBeUsedToMatch":true},{"id":"dew point","displayName":"dew point","required":false,"defaultMatch":false,"display":true,"type":"string","canBeUsedToMatch":true},{"id":"precipitation","displayName":"precipitation","required":false,"defaultMatch":false,"display":true,"type":"string","canBeUsedToMatch":true},{"id":"row_number","displayName":"row_number","required":false,"defaultMatch":false,"display":true,"type":"number","canBeUsedToMatch":true,"readOnly":true,"removed":true}],"attemptToConvertTypes":false,"convertFieldsToString":false},"options":{}},"type":"n8n-nodes-base.googleSheets","typeVersion":4.7,"position":[832,0],"id":"a93cc2cb-32ed-4c23-a472-3d0879631d3a","name":"Update row in sheet","credentials":{"googleSheetsOAuth2Api":{"id":"YGaPHefyc9NONFfU","name":"Google Sheets account"}}},{"parameters":{"assignments":{"assignments":[{"id":"29c985fd-3d2c-4974-a745-0ff8b9d51ac8","name":"Temperature","value":"={{ $json.app_temp }}","type":"number"},{"id":"ad42e2cf-5ce5-4044-9406-a13e66b8a3c1","name":"Cloud","value":"={{ $json.clouds }}","type":"number"},{"id":"dea0809f-9708-409e-8e02-67ffc48a1e53","name":"Dew point","value":"={{ $json.dewpt }}","type":"number"}]},"options":{}},"type":"n8n-nodes-base.set","typeVersion":3.4,"position":[624,0],"id":"48d07b6c-48e3-46cc-a19d-54ff26310916","name":"Edit Fields"}]	{"When clicking ‘Execute workflow’":{"main":[[{"node":"HTTP Request","type":"main","index":0}]]},"HTTP Request":{"main":[[{"node":"Split Out","type":"main","index":0}]]},"Split Out":{"main":[[{"node":"Edit Fields","type":"main","index":0}]]},"Edit Fields":{"main":[[{"node":"Update row in sheet","type":"main","index":0}]]}}	2025-10-29 21:42:24.842+00	2025-11-08 19:33:19.372+00	{"executionOrder":"v1"}	\N	{"HTTP Request":[{"json":{"city_name":"Four Oaks","country_code":"US","data":[{"app_temp":70.9,"clouds":35,"clouds_hi":0,"clouds_low":9,"clouds_mid":9,"datetime":"2025-11-08:18","dewpt":58.6,"dhi":103,"dni":840,"ghi":585,"ozone":263,"pod":"d","pop":0,"precip":0,"pres":1003,"rh":65,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":546.5986,"temp":70.9,"timestamp_local":"2025-11-08T13:00:00","timestamp_utc":"2025-11-08T18:00:00","ts":1762624800,"uv":3,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"NNW","wind_cdir_full":"north-northwest","wind_dir":330,"wind_gust_spd":4.7,"wind_spd":2.7},{"app_temp":71.8,"clouds":34,"clouds_hi":0,"clouds_low":3,"clouds_mid":100,"datetime":"2025-11-08:19","dewpt":58.3,"dhi":96,"dni":798,"ghi":489,"ozone":264,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":62,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":458.78934,"temp":72,"timestamp_local":"2025-11-08T14:00:00","timestamp_utc":"2025-11-08T19:00:00","ts":1762628400,"uv":2,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":320,"wind_gust_spd":4.7,"wind_spd":1.8},{"app_temp":71.8,"clouds":35,"clouds_hi":0,"clouds_low":2,"clouds_mid":100,"datetime":"2025-11-08:20","dewpt":57.7,"dhi":83,"dni":714,"ghi":344,"ozone":265,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":61,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":321.97458,"temp":72,"timestamp_local":"2025-11-08T15:00:00","timestamp_utc":"2025-11-08T20:00:00","ts":1762632000,"uv":2,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"S","wind_cdir_full":"south","wind_dir":180,"wind_gust_spd":4.7,"wind_spd":1.8},{"app_temp":70.9,"clouds":30,"clouds_hi":0,"clouds_low":0,"clouds_mid":9,"datetime":"2025-11-08:21","dewpt":58.3,"dhi":61,"dni":545,"ghi":168,"ozone":266,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":64,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":159.23553,"temp":71.1,"timestamp_local":"2025-11-08T16:00:00","timestamp_utc":"2025-11-08T21:00:00","ts":1762635600,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SSE","wind_cdir_full":"south-southeast","wind_dir":150,"wind_gust_spd":3.8,"wind_spd":0.9},{"app_temp":68.5,"clouds":22,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-08:22","dewpt":59.4,"dhi":15,"dni":85,"ghi":9,"ozone":265,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":72,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":24.27798,"temp":68.7,"timestamp_local":"2025-11-08T17:00:00","timestamp_utc":"2025-11-08T22:00:00","ts":1762639200,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SSE","wind_cdir_full":"south-southeast","wind_dir":150,"wind_gust_spd":2.9,"wind_spd":0.9},{"app_temp":64.9,"clouds":49,"clouds_hi":0,"clouds_low":39,"clouds_mid":0,"datetime":"2025-11-08:23","dewpt":59.5,"dhi":0,"dni":0,"ghi":0,"ozone":266,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":83,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":64.9,"timestamp_local":"2025-11-08T18:00:00","timestamp_utc":"2025-11-08T23:00:00","ts":1762642800,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"E","wind_cdir_full":"east","wind_dir":90,"wind_gust_spd":2,"wind_spd":0.9},{"app_temp":62.2,"clouds":63,"clouds_hi":0,"clouds_low":91,"clouds_mid":0,"datetime":"2025-11-09:00","dewpt":59.5,"dhi":0,"dni":0,"ghi":0,"ozone":265,"pod":"n","pop":0,"precip":0,"pres":1004,"rh":91,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":62.2,"timestamp_local":"2025-11-08T19:00:00","timestamp_utc":"2025-11-09T00:00:00","ts":1762646400,"uv":0,"vis":13.2,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"ENE","wind_cdir_full":"east-northeast","wind_dir":60,"wind_gust_spd":1.3,"wind_spd":0.9},{"app_temp":61,"clouds":50,"clouds_hi":0,"clouds_low":23,"clouds_mid":0,"datetime":"2025-11-09:01","dewpt":59.2,"dhi":0,"dni":0,"ghi":0,"ozone":264,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":94,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61,"timestamp_local":"2025-11-08T20:00:00","timestamp_utc":"2025-11-09T01:00:00","ts":1762650000,"uv":0,"vis":12,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"E","wind_cdir_full":"east","wind_dir":80,"wind_gust_spd":2.2,"wind_spd":0.9},{"app_temp":61,"clouds":65,"clouds_hi":0,"clouds_low":68,"clouds_mid":100,"datetime":"2025-11-09:02","dewpt":59.7,"dhi":0,"dni":0,"ghi":0,"ozone":264,"pod":"n","pop":25,"precip":0.01,"pres":1003,"rh":96,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61,"timestamp_local":"2025-11-08T21:00:00","timestamp_utc":"2025-11-09T02:00:00","ts":1762653600,"uv":0,"vis":10.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"E","wind_cdir_full":"east","wind_dir":100,"wind_gust_spd":2.9,"wind_spd":0.9},{"app_temp":60.6,"clouds":82,"clouds_hi":0,"clouds_low":71,"clouds_mid":64,"datetime":"2025-11-09:03","dewpt":60.1,"dhi":0,"dni":0,"ghi":0,"ozone":265,"pod":"n","pop":40,"precip":0.02,"pres":1003,"rh":98,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":60.6,"timestamp_local":"2025-11-08T22:00:00","timestamp_utc":"2025-11-09T03:00:00","ts":1762657200,"uv":0,"vis":10.7,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"SE","wind_cdir_full":"southeast","wind_dir":130,"wind_gust_spd":2.9,"wind_spd":0.9},{"app_temp":60.1,"clouds":77,"clouds_hi":0,"clouds_low":87,"clouds_mid":87,"datetime":"2025-11-09:04","dewpt":60.1,"dhi":0,"dni":0,"ghi":0,"ozone":266,"pod":"n","pop":40,"precip":0.02,"pres":1003,"rh":100,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":60.3,"timestamp_local":"2025-11-08T23:00:00","timestamp_utc":"2025-11-09T04:00:00","ts":1762660800,"uv":0,"vis":5.9,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"SE","wind_cdir_full":"southeast","wind_dir":130,"wind_gust_spd":3.8,"wind_spd":0.9},{"app_temp":60.6,"clouds":83,"clouds_hi":0,"clouds_low":100,"clouds_mid":81,"datetime":"2025-11-09:05","dewpt":60.6,"dhi":0,"dni":0,"ghi":0,"ozone":265,"pod":"n","pop":80,"precip":0.13,"pres":1003,"rh":100,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":60.6,"timestamp_local":"2025-11-09T00:00:00","timestamp_utc":"2025-11-09T05:00:00","ts":1762664400,"uv":0,"vis":7.6,"weather":{"description":"Light rain","icon":"r01n","code":500},"wind_cdir":"SSE","wind_cdir_full":"south-southeast","wind_dir":150,"wind_gust_spd":3.8,"wind_spd":0.9},{"app_temp":61,"clouds":86,"clouds_hi":0,"clouds_low":58,"clouds_mid":17,"datetime":"2025-11-09:06","dewpt":61,"dhi":0,"dni":0,"ghi":0,"ozone":262,"pod":"n","pop":40,"precip":0.02,"pres":1002,"rh":100,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61,"timestamp_local":"2025-11-09T01:00:00","timestamp_utc":"2025-11-09T06:00:00","ts":1762668000,"uv":0,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"SSE","wind_cdir_full":"south-southeast","wind_dir":160,"wind_gust_spd":4.7,"wind_spd":1.8},{"app_temp":60.4,"clouds":86,"clouds_hi":0,"clouds_low":9,"clouds_mid":0,"datetime":"2025-11-09:07","dewpt":60.4,"dhi":0,"dni":0,"ghi":0,"ozone":262,"pod":"n","pop":50,"precip":0.03,"pres":1002,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":60.4,"timestamp_local":"2025-11-09T02:00:00","timestamp_utc":"2025-11-09T07:00:00","ts":1762671600,"uv":0,"vis":7.6,"weather":{"description":"Drizzle","icon":"d02n","code":301},"wind_cdir":"S","wind_cdir_full":"south","wind_dir":170,"wind_gust_spd":5.6,"wind_spd":1.8},{"app_temp":61.2,"clouds":84,"clouds_hi":0,"clouds_low":13,"clouds_mid":0,"datetime":"2025-11-09:08","dewpt":61.2,"dhi":0,"dni":0,"ghi":0,"ozone":262,"pod":"n","pop":25,"precip":0.01,"pres":1002,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61.2,"timestamp_local":"2025-11-09T03:00:00","timestamp_utc":"2025-11-09T08:00:00","ts":1762675200,"uv":0,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"S","wind_cdir_full":"south","wind_dir":180,"wind_gust_spd":6.5,"wind_spd":2.7},{"app_temp":61.7,"clouds":81,"clouds_hi":0,"clouds_low":88,"clouds_mid":29,"datetime":"2025-11-09:09","dewpt":61.7,"dhi":0,"dni":0,"ghi":0,"ozone":261,"pod":"n","pop":25,"precip":0.01,"pres":1001,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61.7,"timestamp_local":"2025-11-09T04:00:00","timestamp_utc":"2025-11-09T09:00:00","ts":1762678800,"uv":0,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"S","wind_cdir_full":"south","wind_dir":190,"wind_gust_spd":6.7,"wind_spd":2.7},{"app_temp":61.2,"clouds":83,"clouds_hi":0,"clouds_low":100,"clouds_mid":0,"datetime":"2025-11-09:10","dewpt":61.2,"dhi":0,"dni":0,"ghi":0,"ozone":261,"pod":"n","pop":25,"precip":0.01,"pres":1001,"rh":100,"slp":1008,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61.2,"timestamp_local":"2025-11-09T05:00:00","timestamp_utc":"2025-11-09T10:00:00","ts":1762682400,"uv":0,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04n","code":804},"wind_cdir":"S","wind_cdir_full":"south","wind_dir":190,"wind_gust_spd":7.4,"wind_spd":3.6},{"app_temp":61.2,"clouds":69,"clouds_hi":3,"clouds_low":72,"clouds_mid":0,"datetime":"2025-11-09:11","dewpt":61.2,"dhi":0,"dni":0,"ghi":0,"ozone":261,"pod":"n","pop":0,"precip":0,"pres":1001,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":61.2,"timestamp_local":"2025-11-09T06:00:00","timestamp_utc":"2025-11-09T11:00:00","ts":1762686000,"uv":0,"vis":7.6,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"SSW","wind_cdir_full":"south-southwest","wind_dir":200,"wind_gust_spd":8.5,"wind_spd":3.6},{"app_temp":62.1,"clouds":81,"clouds_hi":1,"clouds_low":100,"clouds_mid":0,"datetime":"2025-11-09:12","dewpt":62.1,"dhi":21,"dni":144,"ghi":18,"ozone":262,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":29.926853,"temp":62.1,"timestamp_local":"2025-11-09T07:00:00","timestamp_utc":"2025-11-09T12:00:00","ts":1762689600,"uv":1,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04d","code":804},"wind_cdir":"SSW","wind_cdir_full":"south-southwest","wind_dir":210,"wind_gust_spd":9.4,"wind_spd":4.5},{"app_temp":63.3,"clouds":80,"clouds_hi":0,"clouds_low":42,"clouds_mid":0,"datetime":"2025-11-09:13","dewpt":63.3,"dhi":63,"dni":563,"ghi":182,"ozone":263,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":100,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":96.54679,"temp":63.3,"timestamp_local":"2025-11-09T08:00:00","timestamp_utc":"2025-11-09T13:00:00","ts":1762693200,"uv":1,"vis":7.6,"weather":{"description":"Overcast clouds","icon":"c04d","code":804},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":10.5,"wind_spd":5.4},{"app_temp":66.7,"clouds":83,"clouds_hi":0,"clouds_low":63,"clouds_mid":0,"datetime":"2025-11-09:14","dewpt":65.5,"dhi":84,"dni":722,"ghi":355,"ozone":263,"pod":"d","pop":0,"precip":0,"pres":1002,"rh":99,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":167.35391,"temp":65.7,"timestamp_local":"2025-11-09T09:00:00","timestamp_utc":"2025-11-09T14:00:00","ts":1762696800,"uv":1,"vis":8,"weather":{"description":"Overcast clouds","icon":"c04d","code":804},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":12.3,"wind_spd":6.3},{"app_temp":68.4,"clouds":81,"clouds_hi":5,"clouds_low":100,"clouds_mid":0,"datetime":"2025-11-09:15","dewpt":65.3,"dhi":96,"dni":802,"ghi":496,"ozone":263,"pod":"d","pop":0,"precip":0,"pres":1001,"rh":93,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":252.73817,"temp":67.5,"timestamp_local":"2025-11-09T10:00:00","timestamp_utc":"2025-11-09T15:00:00","ts":1762700400,"uv":1,"vis":9.1,"weather":{"description":"Overcast clouds","icon":"c04d","code":804},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":13.6,"wind_spd":7.2},{"app_temp":70.7,"clouds":63,"clouds_hi":56,"clouds_low":69,"clouds_mid":0,"datetime":"2025-11-09:16","dewpt":65.3,"dhi":103,"dni":841,"ghi":586,"ozone":261,"pod":"d","pop":0,"precip":0,"pres":1001,"rh":85,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":446.9002,"temp":70,"timestamp_local":"2025-11-09T11:00:00","timestamp_utc":"2025-11-09T16:00:00","ts":1762704000,"uv":2,"vis":9.6,"weather":{"description":"Broken clouds","icon":"c03d","code":803},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":15.4,"wind_spd":8.1},{"app_temp":72.3,"clouds":50,"clouds_hi":17,"clouds_low":32,"clouds_mid":0,"datetime":"2025-11-09:17","dewpt":64.6,"dhi":105,"dni":852,"ghi":615,"ozone":261,"pod":"d","pop":0,"precip":0,"pres":1001,"rh":78,"slp":1008,"snow":0,"snow_depth":0,"solar_rad":532.61316,"temp":71.8,"timestamp_local":"2025-11-09T12:00:00","timestamp_utc":"2025-11-09T17:00:00","ts":1762707600,"uv":3,"vis":10.7,"weather":{"description":"Broken clouds","icon":"c03d","code":803},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":16.6,"wind_spd":8.9},{"app_temp":73.9,"clouds":39,"clouds_hi":97,"clouds_low":13,"clouds_mid":0,"datetime":"2025-11-09:18","dewpt":64,"dhi":103,"dni":839,"ghi":581,"ozone":262,"pod":"d","pop":0,"precip":0,"pres":1000,"rh":72,"slp":1007,"snow":0,"snow_depth":0,"solar_rad":531.2312,"temp":73.6,"timestamp_local":"2025-11-09T13:00:00","timestamp_utc":"2025-11-09T18:00:00","ts":1762711200,"uv":3,"vis":13.5,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":16.6,"wind_spd":8.9},{"app_temp":73.9,"clouds":40,"clouds_hi":0,"clouds_low":15,"clouds_mid":0,"datetime":"2025-11-09:19","dewpt":62.4,"dhi":96,"dni":796,"ghi":485,"ozone":262,"pod":"d","pop":45,"precip":0.03,"pres":1000,"rh":68,"slp":1007,"snow":0,"snow_depth":0,"solar_rad":443.7212,"temp":73.8,"timestamp_local":"2025-11-09T14:00:00","timestamp_utc":"2025-11-09T19:00:00","ts":1762714800,"uv":2,"vis":14.9,"weather":{"description":"Thunderstorm with rain","icon":"t02d","code":201},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":16.6,"wind_spd":8.9},{"app_temp":73.9,"clouds":25,"clouds_hi":0,"clouds_low":2,"clouds_mid":0,"datetime":"2025-11-09:20","dewpt":61.7,"dhi":82,"dni":712,"ghi":340,"ozone":267,"pod":"d","pop":35,"precip":0.02,"pres":1000,"rh":66,"slp":1008,"snow":0,"snow_depth":0,"solar_rad":322.5407,"temp":73.8,"timestamp_local":"2025-11-09T15:00:00","timestamp_utc":"2025-11-09T20:00:00","ts":1762718400,"uv":2,"vis":14.7,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":16.6,"wind_spd":8.1},{"app_temp":73.4,"clouds":33,"clouds_hi":0,"clouds_low":0,"clouds_mid":40,"datetime":"2025-11-09:21","dewpt":61.7,"dhi":60,"dni":541,"ghi":165,"ozone":269,"pod":"d","pop":0,"precip":0,"pres":1000,"rh":67,"slp":1007,"snow":0,"snow_depth":0,"solar_rad":154.62637,"temp":73.2,"timestamp_local":"2025-11-09T16:00:00","timestamp_utc":"2025-11-09T21:00:00","ts":1762722000,"uv":1,"vis":13.2,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":15,"wind_spd":7.2},{"app_temp":71.6,"clouds":31,"clouds_hi":91,"clouds_low":1,"clouds_mid":100,"datetime":"2025-11-09:22","dewpt":61.9,"dhi":14,"dni":75,"ghi":8,"ozone":269,"pod":"d","pop":0,"precip":0,"pres":1000,"rh":72,"slp":1007,"snow":0,"snow_depth":0,"solar_rad":21.837938,"temp":71.4,"timestamp_local":"2025-11-09T17:00:00","timestamp_utc":"2025-11-09T22:00:00","ts":1762725600,"uv":1,"vis":11.1,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":13.9,"wind_spd":6.3},{"app_temp":67.5,"clouds":30,"clouds_hi":0,"clouds_low":1,"clouds_mid":96,"datetime":"2025-11-09:23","dewpt":61.2,"dhi":0,"dni":0,"ghi":0,"ozone":273,"pod":"n","pop":0,"precip":0,"pres":1000,"rh":81,"slp":1007,"snow":0,"snow_depth":0,"solar_rad":0,"temp":67.1,"timestamp_local":"2025-11-09T18:00:00","timestamp_utc":"2025-11-09T23:00:00","ts":1762729200,"uv":0,"vis":10.6,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":12.1,"wind_spd":5.4},{"app_temp":64.6,"clouds":23,"clouds_hi":2,"clouds_low":1,"clouds_mid":0,"datetime":"2025-11-10:00","dewpt":60.6,"dhi":0,"dni":0,"ghi":0,"ozone":275,"pod":"n","pop":0,"precip":0,"pres":1000,"rh":87,"slp":1008,"snow":0,"snow_depth":0,"solar_rad":0,"temp":64.6,"timestamp_local":"2025-11-09T19:00:00","timestamp_utc":"2025-11-10T00:00:00","ts":1762732800,"uv":0,"vis":10,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":10.7,"wind_spd":4.5},{"app_temp":62.2,"clouds":40,"clouds_hi":100,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-10:01","dewpt":58.3,"dhi":0,"dni":0,"ghi":0,"ozone":273,"pod":"n","pop":0,"precip":0,"pres":1001,"rh":87,"slp":1008,"snow":0,"snow_depth":0,"solar_rad":0,"temp":62.2,"timestamp_local":"2025-11-09T20:00:00","timestamp_utc":"2025-11-10T01:00:00","ts":1762736400,"uv":0,"vis":9.6,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":260,"wind_gust_spd":11.2,"wind_spd":5.4},{"app_temp":60.8,"clouds":59,"clouds_hi":13,"clouds_low":4,"clouds_mid":1,"datetime":"2025-11-10:02","dewpt":56.8,"dhi":0,"dni":0,"ghi":0,"ozone":270,"pod":"n","pop":0,"precip":0,"pres":1001,"rh":87,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":60.8,"timestamp_local":"2025-11-09T21:00:00","timestamp_utc":"2025-11-10T02:00:00","ts":1762740000,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":270,"wind_gust_spd":11.2,"wind_spd":5.4},{"app_temp":59.2,"clouds":42,"clouds_hi":3,"clouds_low":65,"clouds_mid":0,"datetime":"2025-11-10:03","dewpt":53.1,"dhi":0,"dni":0,"ghi":0,"ozone":270,"pod":"n","pop":0,"precip":0,"pres":1002,"rh":80,"slp":1009,"snow":0,"snow_depth":0,"solar_rad":0,"temp":59.2,"timestamp_local":"2025-11-09T22:00:00","timestamp_utc":"2025-11-10T03:00:00","ts":1762743600,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":270,"wind_gust_spd":11.2,"wind_spd":5.4},{"app_temp":57.4,"clouds":50,"clouds_hi":100,"clouds_low":100,"clouds_mid":2,"datetime":"2025-11-10:04","dewpt":50.5,"dhi":0,"dni":0,"ghi":0,"ozone":270,"pod":"n","pop":0,"precip":0,"pres":1002,"rh":78,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":57.4,"timestamp_local":"2025-11-09T23:00:00","timestamp_utc":"2025-11-10T04:00:00","ts":1762747200,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":286,"wind_gust_spd":11.1,"wind_spd":5.4},{"app_temp":55.6,"clouds":57,"clouds_hi":100,"clouds_low":100,"clouds_mid":35,"datetime":"2025-11-10:05","dewpt":48.4,"dhi":0,"dni":0,"ghi":0,"ozone":273,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":77,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":55.6,"timestamp_local":"2025-11-10T00:00:00","timestamp_utc":"2025-11-10T05:00:00","ts":1762750800,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":303,"wind_gust_spd":11,"wind_spd":5.4},{"app_temp":53.8,"clouds":65,"clouds_hi":0,"clouds_low":100,"clouds_mid":100,"datetime":"2025-11-10:06","dewpt":46,"dhi":0,"dni":0,"ghi":0,"ozone":273,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":75,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":53.8,"timestamp_local":"2025-11-10T01:00:00","timestamp_utc":"2025-11-10T06:00:00","ts":1762754400,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":320,"wind_gust_spd":11,"wind_spd":5.4},{"app_temp":52,"clouds":61,"clouds_hi":8,"clouds_low":11,"clouds_mid":100,"datetime":"2025-11-10:07","dewpt":44.2,"dhi":0,"dni":0,"ghi":0,"ozone":275,"pod":"n","pop":0,"precip":0,"pres":1002,"rh":75,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":52,"timestamp_local":"2025-11-10T02:00:00","timestamp_utc":"2025-11-10T07:00:00","ts":1762758000,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":323,"wind_gust_spd":11.3,"wind_spd":6},{"app_temp":50.2,"clouds":56,"clouds_hi":0,"clouds_low":100,"clouds_mid":100,"datetime":"2025-11-10:08","dewpt":42.3,"dhi":0,"dni":0,"ghi":0,"ozone":277,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":74,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":50.2,"timestamp_local":"2025-11-10T03:00:00","timestamp_utc":"2025-11-10T08:00:00","ts":1762761600,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":326,"wind_gust_spd":11.7,"wind_spd":6.6},{"app_temp":48.4,"clouds":52,"clouds_hi":0,"clouds_low":1,"clouds_mid":8,"datetime":"2025-11-10:09","dewpt":40.5,"dhi":0,"dni":0,"ghi":0,"ozone":281,"pod":"n","pop":0,"precip":0,"pres":1002,"rh":74,"slp":1010,"snow":0,"snow_depth":0,"solar_rad":0,"temp":48.4,"timestamp_local":"2025-11-10T04:00:00","timestamp_utc":"2025-11-10T09:00:00","ts":1762765200,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"NNW","wind_cdir_full":"north-northwest","wind_dir":330,"wind_gust_spd":12.1,"wind_spd":7.2},{"app_temp":46.9,"clouds":45,"clouds_hi":0,"clouds_low":0,"clouds_mid":26,"datetime":"2025-11-10:10","dewpt":39.2,"dhi":0,"dni":0,"ghi":0,"ozone":282,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":74,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":46.9,"timestamp_local":"2025-11-10T05:00:00","timestamp_utc":"2025-11-10T10:00:00","ts":1762768800,"uv":0,"vis":14.9,"weather":{"description":"Broken clouds","icon":"c03n","code":803},"wind_cdir":"NNW","wind_cdir_full":"north-northwest","wind_dir":330,"wind_gust_spd":12,"wind_spd":6.8},{"app_temp":45.5,"clouds":39,"clouds_hi":0,"clouds_low":0,"clouds_mid":37,"datetime":"2025-11-10:11","dewpt":38.1,"dhi":0,"dni":0,"ghi":0,"ozone":282,"pod":"n","pop":0,"precip":0,"pres":1003,"rh":75,"slp":1011,"snow":0,"snow_depth":0,"solar_rad":0,"temp":45.5,"timestamp_local":"2025-11-10T06:00:00","timestamp_utc":"2025-11-10T11:00:00","ts":1762772400,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"NNW","wind_cdir_full":"north-northwest","wind_dir":330,"wind_gust_spd":11.9,"wind_spd":6.6},{"app_temp":40.5,"clouds":32,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-10:12","dewpt":36.7,"dhi":20,"dni":132,"ghi":16,"ozone":284,"pod":"d","pop":0,"precip":0,"pres":1004,"rh":75,"slp":1012,"snow":0,"snow_depth":0,"solar_rad":35.483665,"temp":44.1,"timestamp_local":"2025-11-10T07:00:00","timestamp_utc":"2025-11-10T12:00:00","ts":1762776000,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"NNW","wind_cdir_full":"north-northwest","wind_dir":330,"wind_gust_spd":11.9,"wind_spd":6.3},{"app_temp":45.5,"clouds":26,"clouds_hi":0,"clouds_low":18,"clouds_mid":0,"datetime":"2025-11-10:13","dewpt":36.3,"dhi":62,"dni":558,"ghi":178,"ozone":290,"pod":"d","pop":0,"precip":0,"pres":1006,"rh":70,"slp":1014,"snow":0,"snow_depth":0,"solar_rad":176.57246,"temp":45.5,"timestamp_local":"2025-11-10T08:00:00","timestamp_utc":"2025-11-10T13:00:00","ts":1762779600,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":326,"wind_gust_spd":13.5,"wind_spd":7.4},{"app_temp":46.9,"clouds":21,"clouds_hi":0,"clouds_low":2,"clouds_mid":0,"datetime":"2025-11-10:14","dewpt":35.4,"dhi":84,"dni":719,"ghi":351,"ozone":290,"pod":"d","pop":0,"precip":0,"pres":1007,"rh":64,"slp":1015,"snow":0,"snow_depth":0,"solar_rad":349.76645,"temp":46.9,"timestamp_local":"2025-11-10T09:00:00","timestamp_utc":"2025-11-10T14:00:00","ts":1762783200,"uv":2,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":323,"wind_gust_spd":15.1,"wind_spd":8.6},{"app_temp":48.4,"clouds":15,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-10:15","dewpt":34.9,"dhi":96,"dni":800,"ghi":492,"ozone":288,"pod":"d","pop":0,"precip":0,"pres":1007,"rh":59,"slp":1015,"snow":0,"snow_depth":0,"solar_rad":491.31027,"temp":48.6,"timestamp_local":"2025-11-10T10:00:00","timestamp_utc":"2025-11-10T15:00:00","ts":1762786800,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":320,"wind_gust_spd":16.8,"wind_spd":9.8},{"app_temp":49.5,"clouds":17,"clouds_hi":0,"clouds_low":1,"clouds_mid":0,"datetime":"2025-11-10:16","dewpt":34,"dhi":103,"dni":839,"ghi":582,"ozone":294,"pod":"d","pop":0,"precip":0,"pres":1006,"rh":55,"slp":1014,"snow":0,"snow_depth":0,"solar_rad":580.76746,"temp":49.5,"timestamp_local":"2025-11-10T11:00:00","timestamp_utc":"2025-11-10T16:00:00","ts":1762790400,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":313,"wind_gust_spd":16.9,"wind_spd":9.8},{"app_temp":50.5,"clouds":18,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-10:17","dewpt":33.6,"dhi":105,"dni":851,"ghi":611,"ozone":298,"pod":"d","pop":0,"precip":0,"pres":1006,"rh":52,"slp":1014,"snow":0,"snow_depth":0,"solar_rad":609.38165,"temp":50.5,"timestamp_local":"2025-11-10T12:00:00","timestamp_utc":"2025-11-10T17:00:00","ts":1762794000,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"NW","wind_cdir_full":"northwest","wind_dir":306,"wind_gust_spd":17.1,"wind_spd":9.8},{"app_temp":51.6,"clouds":20,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-10:18","dewpt":32.7,"dhi":103,"dni":837,"ghi":576,"ozone":299,"pod":"d","pop":0,"precip":0,"pres":1005,"rh":48,"slp":1012,"snow":0,"snow_depth":0,"solar_rad":574.21,"temp":51.6,"timestamp_local":"2025-11-10T13:00:00","timestamp_utc":"2025-11-10T18:00:00","ts":1762797600,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":300,"wind_gust_spd":17.2,"wind_spd":9.8},{"app_temp":51.1,"clouds":23,"clouds_hi":0,"clouds_low":47,"clouds_mid":0,"datetime":"2025-11-10:19","dewpt":31.1,"dhi":95,"dni":795,"ghi":481,"ozone":300,"pod":"d","pop":0,"precip":0,"pres":1005,"rh":46,"slp":1013,"snow":0,"snow_depth":0,"solar_rad":478.69577,"temp":51.1,"timestamp_local":"2025-11-10T14:00:00","timestamp_utc":"2025-11-10T19:00:00","ts":1762801200,"uv":3,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":296,"wind_gust_spd":17.1,"wind_spd":9.8},{"app_temp":50.5,"clouds":25,"clouds_hi":0,"clouds_low":59,"clouds_mid":0,"datetime":"2025-11-10:20","dewpt":29.5,"dhi":82,"dni":709,"ghi":337,"ozone":304,"pod":"d","pop":0,"precip":0,"pres":1005,"rh":44,"slp":1013,"snow":0,"snow_depth":0,"solar_rad":334.1342,"temp":50.5,"timestamp_local":"2025-11-10T15:00:00","timestamp_utc":"2025-11-10T20:00:00","ts":1762804800,"uv":2,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":293,"wind_gust_spd":17.1,"wind_spd":9.8},{"app_temp":49.8,"clouds":28,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-10:21","dewpt":27.7,"dhi":60,"dni":537,"ghi":163,"ozone":311,"pod":"d","pop":0,"precip":0,"pres":1006,"rh":42,"slp":1014,"snow":0,"snow_depth":0,"solar_rad":160.59032,"temp":49.8,"timestamp_local":"2025-11-10T16:00:00","timestamp_utc":"2025-11-10T21:00:00","ts":1762808400,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":290,"wind_gust_spd":17,"wind_spd":9.8},{"app_temp":47.1,"clouds":30,"clouds_hi":0,"clouds_low":4,"clouds_mid":0,"datetime":"2025-11-10:22","dewpt":27.3,"dhi":13,"dni":65,"ghi":7,"ozone":316,"pod":"d","pop":0,"precip":0,"pres":1007,"rh":46,"slp":1015,"snow":0,"snow_depth":0,"solar_rad":20.19124,"temp":47.1,"timestamp_local":"2025-11-10T17:00:00","timestamp_utc":"2025-11-10T22:00:00","ts":1762812000,"uv":1,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02d","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":293,"wind_gust_spd":16.4,"wind_spd":8.9},{"app_temp":39.7,"clouds":33,"clouds_hi":0,"clouds_low":44,"clouds_mid":0,"datetime":"2025-11-10:23","dewpt":26.8,"dhi":0,"dni":0,"ghi":0,"ozone":319,"pod":"n","pop":0,"precip":0,"pres":1007,"rh":50,"slp":1015,"snow":0,"snow_depth":0,"solar_rad":0,"temp":44.2,"timestamp_local":"2025-11-10T18:00:00","timestamp_utc":"2025-11-10T23:00:00","ts":1762815600,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":296,"wind_gust_spd":15.8,"wind_spd":8.1},{"app_temp":36.7,"clouds":35,"clouds_hi":0,"clouds_low":98,"clouds_mid":0,"datetime":"2025-11-11:00","dewpt":26.1,"dhi":0,"dni":0,"ghi":0,"ozone":326,"pod":"n","pop":0,"precip":0,"pres":1008,"rh":54,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":0,"temp":41.4,"timestamp_local":"2025-11-10T19:00:00","timestamp_utc":"2025-11-11T00:00:00","ts":1762819200,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":300,"wind_gust_spd":15.2,"wind_spd":7.2},{"app_temp":34.5,"clouds":34,"clouds_hi":0,"clouds_low":47,"clouds_mid":0,"datetime":"2025-11-11:01","dewpt":24.4,"dhi":0,"dni":0,"ghi":0,"ozone":336,"pod":"n","pop":0,"precip":0,"pres":1009,"rh":54,"slp":1017,"snow":0,"snow_depth":0,"solar_rad":0,"temp":39.7,"timestamp_local":"2025-11-10T20:00:00","timestamp_utc":"2025-11-11T01:00:00","ts":1762822800,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":296,"wind_gust_spd":15.2,"wind_spd":7.4},{"app_temp":32.4,"clouds":34,"clouds_hi":0,"clouds_low":98,"clouds_mid":0,"datetime":"2025-11-11:02","dewpt":23.4,"dhi":0,"dni":0,"ghi":0,"ozone":341,"pod":"n","pop":0,"precip":0,"pres":1010,"rh":55,"slp":1018,"snow":0,"snow_depth":0,"solar_rad":0,"temp":38.1,"timestamp_local":"2025-11-10T21:00:00","timestamp_utc":"2025-11-11T02:00:00","ts":1762826400,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":293,"wind_gust_spd":15.2,"wind_spd":7.7},{"app_temp":30.2,"clouds":33,"clouds_hi":0,"clouds_low":100,"clouds_mid":0,"datetime":"2025-11-11:03","dewpt":21.9,"dhi":0,"dni":0,"ghi":0,"ozone":342,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":55,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":36.5,"timestamp_local":"2025-11-10T22:00:00","timestamp_utc":"2025-11-11T03:00:00","ts":1762830000,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":290,"wind_gust_spd":15.2,"wind_spd":8.1},{"app_temp":28.9,"clouds":30,"clouds_hi":0,"clouds_low":85,"clouds_mid":0,"datetime":"2025-11-11:04","dewpt":21,"dhi":0,"dni":0,"ghi":0,"ozone":345,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":56,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":35.2,"timestamp_local":"2025-11-10T23:00:00","timestamp_utc":"2025-11-11T04:00:00","ts":1762833600,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":286,"wind_gust_spd":14.8,"wind_spd":7.7},{"app_temp":27.5,"clouds":28,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:05","dewpt":19.9,"dhi":0,"dni":0,"ghi":0,"ozone":350,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":56,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":34,"timestamp_local":"2025-11-11T00:00:00","timestamp_utc":"2025-11-11T05:00:00","ts":1762837200,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":283,"wind_gust_spd":14.3,"wind_spd":7.4},{"app_temp":26.2,"clouds":25,"clouds_hi":0,"clouds_low":1,"clouds_mid":0,"datetime":"2025-11-11:06","dewpt":19.2,"dhi":0,"dni":0,"ghi":0,"ozone":356,"pod":"n","pop":0,"precip":0,"pres":1012,"rh":57,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":0,"temp":32.7,"timestamp_local":"2025-11-11T01:00:00","timestamp_utc":"2025-11-11T06:00:00","ts":1762840800,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":13.9,"wind_spd":7.2},{"app_temp":25.5,"clouds":22,"clouds_hi":0,"clouds_low":4,"clouds_mid":0,"datetime":"2025-11-11:07","dewpt":18.7,"dhi":0,"dni":0,"ghi":0,"ozone":367,"pod":"n","pop":0,"precip":0,"pres":1012,"rh":57,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":0,"temp":32.2,"timestamp_local":"2025-11-11T02:00:00","timestamp_utc":"2025-11-11T07:00:00","ts":1762844400,"uv":0,"vis":14.9,"weather":{"description":"Scattered clouds","icon":"c02n","code":802},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":14.2,"wind_spd":7.4},{"app_temp":24.8,"clouds":19,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:08","dewpt":18.7,"dhi":0,"dni":0,"ghi":0,"ozone":379,"pod":"n","pop":0,"precip":0,"pres":1012,"rh":58,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":0,"temp":31.8,"timestamp_local":"2025-11-11T03:00:00","timestamp_utc":"2025-11-11T08:00:00","ts":1762848000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":14.5,"wind_spd":7.7},{"app_temp":23.9,"clouds":16,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-11:09","dewpt":18.3,"dhi":0,"dni":0,"ghi":0,"ozone":385,"pod":"n","pop":0,"precip":0,"pres":1013,"rh":58,"slp":1021,"snow":0,"snow_depth":0,"solar_rad":0,"temp":31.3,"timestamp_local":"2025-11-11T04:00:00","timestamp_utc":"2025-11-11T09:00:00","ts":1762851600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":14.8,"wind_spd":8.1},{"app_temp":24.3,"clouds":11,"clouds_hi":0,"clouds_low":5,"clouds_mid":0,"datetime":"2025-11-11:10","dewpt":18.3,"dhi":0,"dni":0,"ghi":0,"ozone":387,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":58,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":31.3,"timestamp_local":"2025-11-11T05:00:00","timestamp_utc":"2025-11-11T10:00:00","ts":1762855200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":14.5,"wind_spd":7.7},{"app_temp":24.4,"clouds":7,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:11","dewpt":18.3,"dhi":0,"dni":0,"ghi":0,"ozone":388,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":58,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":31.3,"timestamp_local":"2025-11-11T06:00:00","timestamp_utc":"2025-11-11T11:00:00","ts":1762858800,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":14.2,"wind_spd":7.4},{"app_temp":24.6,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:12","dewpt":18.3,"dhi":19,"dni":119,"ghi":14,"ozone":389,"pod":"d","pop":0,"precip":0,"pres":1015,"rh":58,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":32.68998,"temp":31.5,"timestamp_local":"2025-11-11T07:00:00","timestamp_utc":"2025-11-11T12:00:00","ts":1762862400,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":13.9,"wind_spd":7.2},{"app_temp":27.3,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:13","dewpt":18.9,"dhi":62,"dni":554,"ghi":175,"ozone":387,"pod":"d","pop":0,"precip":0,"pres":1017,"rh":53,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":174.70975,"temp":34.2,"timestamp_local":"2025-11-11T08:00:00","timestamp_utc":"2025-11-11T13:00:00","ts":1762866000,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":283,"wind_gust_spd":15.2,"wind_spd":8.1},{"app_temp":30.2,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:14","dewpt":18.5,"dhi":83,"dni":717,"ghi":347,"ozone":378,"pod":"d","pop":0,"precip":0,"pres":1017,"rh":47,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":347.1595,"temp":36.7,"timestamp_local":"2025-11-11T09:00:00","timestamp_utc":"2025-11-11T14:00:00","ts":1762869600,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":286,"wind_gust_spd":16.6,"wind_spd":8.9},{"app_temp":33.1,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:15","dewpt":18.3,"dhi":96,"dni":798,"ghi":488,"ozone":360,"pod":"d","pop":0,"precip":0,"pres":1017,"rh":42,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":487.67926,"temp":39.4,"timestamp_local":"2025-11-11T10:00:00","timestamp_utc":"2025-11-11T15:00:00","ts":1762873200,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":290,"wind_gust_spd":17.9,"wind_spd":9.8},{"app_temp":35.6,"clouds":4,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:16","dewpt":19,"dhi":103,"dni":838,"ghi":578,"ozone":353,"pod":"d","pop":0,"precip":0,"pres":1017,"rh":40,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":577.548,"temp":41.5,"timestamp_local":"2025-11-11T11:00:00","timestamp_utc":"2025-11-11T16:00:00","ts":1762876800,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":286,"wind_gust_spd":18.2,"wind_spd":9.8},{"app_temp":38.1,"clouds":7,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:17","dewpt":19.8,"dhi":105,"dni":849,"ghi":607,"ozone":349,"pod":"d","pop":0,"precip":0,"pres":1016,"rh":38,"slp":1024,"snow":0,"snow_depth":0,"solar_rad":606.71545,"temp":43.5,"timestamp_local":"2025-11-11T12:00:00","timestamp_utc":"2025-11-11T17:00:00","ts":1762880400,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":283,"wind_gust_spd":18.5,"wind_spd":9.8},{"app_temp":45.7,"clouds":9,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:18","dewpt":20.3,"dhi":102,"dni":836,"ghi":572,"ozone":347,"pod":"d","pop":0,"precip":0,"pres":1015,"rh":36,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":572.1067,"temp":45.7,"timestamp_local":"2025-11-11T13:00:00","timestamp_utc":"2025-11-11T18:00:00","ts":1762884000,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":18.8,"wind_spd":9.8},{"app_temp":46.2,"clouds":7,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:19","dewpt":20.8,"dhi":95,"dni":793,"ghi":478,"ozone":343,"pod":"d","pop":0,"precip":0,"pres":1015,"rh":36,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":477.5891,"temp":46.2,"timestamp_local":"2025-11-11T14:00:00","timestamp_utc":"2025-11-11T19:00:00","ts":1762887600,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":273,"wind_gust_spd":18,"wind_spd":9.2},{"app_temp":46.8,"clouds":5,"clouds_hi":3,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:20","dewpt":21.4,"dhi":82,"dni":707,"ghi":334,"ozone":337,"pod":"d","pop":0,"precip":0,"pres":1015,"rh":36,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":333.54868,"temp":46.8,"timestamp_local":"2025-11-11T15:00:00","timestamp_utc":"2025-11-11T20:00:00","ts":1762891200,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":266,"wind_gust_spd":17.1,"wind_spd":8.6},{"app_temp":47.5,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:21","dewpt":21.9,"dhi":59,"dni":533,"ghi":160,"ozone":336,"pod":"d","pop":0,"precip":0,"pres":1015,"rh":36,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":159.70905,"temp":47.5,"timestamp_local":"2025-11-11T16:00:00","timestamp_utc":"2025-11-11T21:00:00","ts":1762894800,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":260,"wind_gust_spd":16.3,"wind_spd":8.1},{"app_temp":41,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:22","dewpt":23.2,"dhi":12,"dni":55,"ghi":6,"ozone":334,"pod":"d","pop":0,"precip":0,"pres":1016,"rh":42,"slp":1024,"snow":0,"snow_depth":0,"solar_rad":18.169977,"temp":44.8,"timestamp_local":"2025-11-11T17:00:00","timestamp_utc":"2025-11-11T22:00:00","ts":1762898400,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":250,"wind_gust_spd":14.2,"wind_spd":6.8},{"app_temp":38.5,"clouds":2,"clouds_hi":1,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-11:23","dewpt":23.9,"dhi":0,"dni":0,"ghi":0,"ozone":330,"pod":"n","pop":0,"precip":0,"pres":1016,"rh":48,"slp":1024,"snow":0,"snow_depth":0,"solar_rad":0,"temp":42.1,"timestamp_local":"2025-11-11T18:00:00","timestamp_utc":"2025-11-11T23:00:00","ts":1762902000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":240,"wind_gust_spd":12.1,"wind_spd":5.7},{"app_temp":36.3,"clouds":2,"clouds_hi":98,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:00","dewpt":24.3,"dhi":0,"dni":0,"ghi":0,"ozone":325,"pod":"n","pop":0,"precip":0,"pres":1017,"rh":54,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":0,"temp":39.6,"timestamp_local":"2025-11-11T19:00:00","timestamp_utc":"2025-11-12T00:00:00","ts":1762905600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":10.1,"wind_spd":4.5},{"app_temp":34.2,"clouds":3,"clouds_hi":5,"clouds_low":4,"clouds_mid":1,"datetime":"2025-11-12:01","dewpt":24.4,"dhi":0,"dni":0,"ghi":0,"ozone":321,"pod":"n","pop":0,"precip":0,"pres":1017,"rh":56,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":0,"temp":38.8,"timestamp_local":"2025-11-11T20:00:00","timestamp_utc":"2025-11-12T01:00:00","ts":1762909200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":226,"wind_gust_spd":8.2,"wind_spd":6.4},{"app_temp":32.2,"clouds":3,"clouds_hi":5,"clouds_low":5,"clouds_mid":5,"datetime":"2025-11-12:02","dewpt":24.3,"dhi":0,"dni":0,"ghi":0,"ozone":317,"pod":"n","pop":0,"precip":0,"pres":1017,"rh":57,"slp":1025,"snow":0,"snow_depth":0,"solar_rad":0,"temp":38.1,"timestamp_local":"2025-11-11T21:00:00","timestamp_utc":"2025-11-12T02:00:00","ts":1762912800,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":223,"wind_gust_spd":6.3,"wind_spd":8.3},{"app_temp":30.4,"clouds":4,"clouds_hi":4,"clouds_low":0,"clouds_mid":5,"datetime":"2025-11-12:03","dewpt":24.4,"dhi":0,"dni":0,"ghi":0,"ozone":314,"pod":"n","pop":0,"precip":0,"pres":1016,"rh":59,"slp":1024,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.4,"timestamp_local":"2025-11-11T22:00:00","timestamp_utc":"2025-11-12T03:00:00","ts":1762916400,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":4.5,"wind_spd":10.3},{"app_temp":31.3,"clouds":8,"clouds_hi":5,"clouds_low":0,"clouds_mid":51,"datetime":"2025-11-12:04","dewpt":24.4,"dhi":0,"dni":0,"ghi":0,"ozone":312,"pod":"n","pop":0,"precip":0,"pres":1016,"rh":59,"slp":1024,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.6,"timestamp_local":"2025-11-11T23:00:00","timestamp_utc":"2025-11-12T04:00:00","ts":1762920000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":6.9,"wind_spd":8.6},{"app_temp":32.2,"clouds":11,"clouds_hi":14,"clouds_low":0,"clouds_mid":99,"datetime":"2025-11-12:05","dewpt":24.1,"dhi":0,"dni":0,"ghi":0,"ozone":309,"pod":"n","pop":0,"precip":0,"pres":1015,"rh":58,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.6,"timestamp_local":"2025-11-12T00:00:00","timestamp_utc":"2025-11-12T05:00:00","ts":1762923600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":9.4,"wind_spd":7},{"app_temp":33.3,"clouds":15,"clouds_hi":5,"clouds_low":0,"clouds_mid":50,"datetime":"2025-11-12:06","dewpt":24.1,"dhi":0,"dni":0,"ghi":0,"ozone":308,"pod":"n","pop":0,"precip":0,"pres":1015,"rh":58,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.6,"timestamp_local":"2025-11-12T01:00:00","timestamp_utc":"2025-11-12T06:00:00","ts":1762927200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":11.9,"wind_spd":5.4},{"app_temp":31.5,"clouds":13,"clouds_hi":0,"clouds_low":0,"clouds_mid":14,"datetime":"2025-11-12:07","dewpt":23.7,"dhi":0,"dni":0,"ghi":0,"ozone":307,"pod":"n","pop":0,"precip":0,"pres":1015,"rh":57,"slp":1023,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.6,"timestamp_local":"2025-11-12T02:00:00","timestamp_utc":"2025-11-12T07:00:00","ts":1762930800,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":10.3,"wind_spd":8.1},{"app_temp":30,"clouds":11,"clouds_hi":0,"clouds_low":0,"clouds_mid":5,"datetime":"2025-11-12:08","dewpt":23.7,"dhi":0,"dni":0,"ghi":0,"ozone":307,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":57,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.4,"timestamp_local":"2025-11-12T03:00:00","timestamp_utc":"2025-11-12T08:00:00","ts":1762934400,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":8.7,"wind_spd":10.9},{"app_temp":28.9,"clouds":9,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:09","dewpt":23.2,"dhi":0,"dni":0,"ghi":0,"ozone":306,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":56,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.4,"timestamp_local":"2025-11-12T04:00:00","timestamp_utc":"2025-11-12T09:00:00","ts":1762938000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":7.2,"wind_spd":13.6},{"app_temp":29.5,"clouds":9,"clouds_hi":5,"clouds_low":0,"clouds_mid":4,"datetime":"2025-11-12:10","dewpt":23,"dhi":0,"dni":0,"ghi":0,"ozone":306,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":56,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37.2,"timestamp_local":"2025-11-12T05:00:00","timestamp_utc":"2025-11-12T10:00:00","ts":1762941600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":9.9,"wind_spd":11.8},{"app_temp":30,"clouds":10,"clouds_hi":5,"clouds_low":0,"clouds_mid":28,"datetime":"2025-11-12:11","dewpt":23.4,"dhi":0,"dni":0,"ghi":0,"ozone":304,"pod":"n","pop":0,"precip":0,"pres":1014,"rh":57,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":0,"temp":37,"timestamp_local":"2025-11-12T06:00:00","timestamp_utc":"2025-11-12T11:00:00","ts":1762945200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":12.7,"wind_spd":9.9},{"app_temp":30.7,"clouds":10,"clouds_hi":5,"clouds_low":0,"clouds_mid":35,"datetime":"2025-11-12:12","dewpt":23.2,"dhi":18,"dni":106,"ghi":12,"ozone":302,"pod":"d","pop":0,"precip":0,"pres":1014,"rh":57,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":29.665642,"temp":36.9,"timestamp_local":"2025-11-12T07:00:00","timestamp_utc":"2025-11-12T12:00:00","ts":1762948800,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":220,"wind_gust_spd":15.4,"wind_spd":8.1},{"app_temp":34,"clouds":8,"clouds_hi":7,"clouds_low":0,"clouds_mid":20,"datetime":"2025-11-12:13","dewpt":25,"dhi":61,"dni":549,"ghi":171,"ozone":303,"pod":"d","pop":0,"precip":0,"pres":1014,"rh":53,"slp":1022,"snow":0,"snow_depth":0,"solar_rad":171.11523,"temp":40.6,"timestamp_local":"2025-11-12T08:00:00","timestamp_utc":"2025-11-12T13:00:00","ts":1762952400,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":223,"wind_gust_spd":13.9,"wind_spd":11.5},{"app_temp":37.6,"clouds":5,"clouds_hi":0,"clouds_low":0,"clouds_mid":82,"datetime":"2025-11-12:14","dewpt":27.1,"dhi":83,"dni":714,"ghi":343,"ozone":305,"pod":"d","pop":0,"precip":0,"pres":1013,"rh":50,"slp":1021,"snow":0,"snow_depth":0,"solar_rad":343.08554,"temp":44.6,"timestamp_local":"2025-11-12T09:00:00","timestamp_utc":"2025-11-12T14:00:00","ts":1762956000,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":226,"wind_gust_spd":12.3,"wind_spd":15.1},{"app_temp":48.4,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":5,"datetime":"2025-11-12:15","dewpt":28.6,"dhi":96,"dni":796,"ghi":483,"ozone":302,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":46,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":483.38712,"temp":48.4,"timestamp_local":"2025-11-12T10:00:00","timestamp_utc":"2025-11-12T15:00:00","ts":1762959600,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":10.7,"wind_spd":18.6},{"app_temp":51.4,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:16","dewpt":30.2,"dhi":102,"dni":836,"ghi":573,"ozone":301,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":44,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":573.2066,"temp":51.4,"timestamp_local":"2025-11-12T11:00:00","timestamp_utc":"2025-11-12T16:00:00","ts":1762963200,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":13.8,"wind_spd":15.9},{"app_temp":54.3,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:17","dewpt":31.8,"dhi":105,"dni":848,"ghi":603,"ozone":297,"pod":"d","pop":0,"precip":0,"pres":1011,"rh":42,"slp":1018,"snow":0,"snow_depth":0,"solar_rad":602.5064,"temp":54.3,"timestamp_local":"2025-11-12T12:00:00","timestamp_utc":"2025-11-12T17:00:00","ts":1762966800,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":16.8,"wind_spd":13.3},{"app_temp":57.4,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:18","dewpt":33.3,"dhi":102,"dni":834,"ghi":568,"ozone":296,"pod":"d","pop":0,"precip":0,"pres":1009,"rh":40,"slp":1017,"snow":0,"snow_depth":0,"solar_rad":568.1966,"temp":57.4,"timestamp_local":"2025-11-12T13:00:00","timestamp_utc":"2025-11-12T18:00:00","ts":1762970400,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":19.9,"wind_spd":10.7},{"app_temp":57.7,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:19","dewpt":33.6,"dhi":95,"dni":791,"ghi":474,"ozone":298,"pod":"d","pop":0,"precip":0,"pres":1008,"rh":40,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":473.8981,"temp":57.7,"timestamp_local":"2025-11-12T14:00:00","timestamp_utc":"2025-11-12T19:00:00","ts":1762974000,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":16.6,"wind_spd":13.4},{"app_temp":58.3,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:20","dewpt":34.7,"dhi":81,"dni":705,"ghi":330,"ozone":299,"pod":"d","pop":0,"precip":0,"pres":1008,"rh":41,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":330.23917,"temp":58.3,"timestamp_local":"2025-11-12T15:00:00","timestamp_utc":"2025-11-12T20:00:00","ts":1762977600,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":13.2,"wind_spd":16.1},{"app_temp":58.8,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:21","dewpt":35.1,"dhi":59,"dni":529,"ghi":157,"ozone":301,"pod":"d","pop":0,"precip":0,"pres":1008,"rh":41,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":156.98978,"temp":58.8,"timestamp_local":"2025-11-12T16:00:00","timestamp_utc":"2025-11-12T21:00:00","ts":1762981200,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":9.8,"wind_spd":18.8},{"app_temp":56.1,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:22","dewpt":36.1,"dhi":11,"dni":46,"ghi":5,"ozone":302,"pod":"d","pop":0,"precip":0,"pres":1008,"rh":47,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":16.159992,"temp":56.1,"timestamp_local":"2025-11-12T17:00:00","timestamp_utc":"2025-11-12T22:00:00","ts":1762984800,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":11.9,"wind_spd":14.9},{"app_temp":53.4,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-12:23","dewpt":37.2,"dhi":0,"dni":0,"ghi":0,"ozone":303,"pod":"n","pop":0,"precip":0,"pres":1009,"rh":54,"slp":1016,"snow":0,"snow_depth":0,"solar_rad":0,"temp":53.4,"timestamp_local":"2025-11-12T18:00:00","timestamp_utc":"2025-11-12T23:00:00","ts":1762988400,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":13.9,"wind_spd":11},{"app_temp":50.9,"clouds":2,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:00","dewpt":37.4,"dhi":0,"dni":0,"ghi":0,"ozone":305,"pod":"n","pop":0,"precip":0,"pres":1009,"rh":60,"slp":1017,"snow":0,"snow_depth":0,"solar_rad":0,"temp":50.9,"timestamp_local":"2025-11-12T19:00:00","timestamp_utc":"2025-11-13T00:00:00","ts":1762992000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":230,"wind_gust_spd":15.9,"wind_spd":7.2},{"app_temp":50.2,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:01","dewpt":38.1,"dhi":0,"dni":0,"ghi":0,"ozone":308,"pod":"n","pop":0,"precip":0,"pres":1010,"rh":63,"slp":1018,"snow":0,"snow_depth":0,"solar_rad":0,"temp":50.2,"timestamp_local":"2025-11-12T20:00:00","timestamp_utc":"2025-11-13T01:00:00","ts":1762995600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"SW","wind_cdir_full":"southwest","wind_dir":236,"wind_gust_spd":12.4,"wind_spd":9.1},{"app_temp":49.6,"clouds":3,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:02","dewpt":38.5,"dhi":0,"dni":0,"ghi":0,"ozone":308,"pod":"n","pop":0,"precip":0,"pres":1010,"rh":65,"slp":1018,"snow":0,"snow_depth":0,"solar_rad":0,"temp":49.6,"timestamp_local":"2025-11-12T21:00:00","timestamp_utc":"2025-11-13T02:00:00","ts":1762999200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":243,"wind_gust_spd":8.9,"wind_spd":11},{"app_temp":49.1,"clouds":4,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:03","dewpt":39,"dhi":0,"dni":0,"ghi":0,"ozone":308,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":68,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":49.1,"timestamp_local":"2025-11-12T22:00:00","timestamp_utc":"2025-11-13T03:00:00","ts":1763002800,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":250,"wind_gust_spd":5.4,"wind_spd":13},{"app_temp":48.4,"clouds":5,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:04","dewpt":39,"dhi":0,"dni":0,"ghi":0,"ozone":307,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":70,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":48.4,"timestamp_local":"2025-11-12T23:00:00","timestamp_utc":"2025-11-13T04:00:00","ts":1763006400,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":253,"wind_gust_spd":6.9,"wind_spd":10.1},{"app_temp":47.7,"clouds":7,"clouds_hi":28,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:05","dewpt":39.2,"dhi":0,"dni":0,"ghi":0,"ozone":304,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":72,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":47.7,"timestamp_local":"2025-11-13T00:00:00","timestamp_utc":"2025-11-13T05:00:00","ts":1763010000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WSW","wind_cdir_full":"west-southwest","wind_dir":256,"wind_gust_spd":8.5,"wind_spd":7.3},{"app_temp":47.1,"clouds":8,"clouds_hi":84,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:06","dewpt":39.2,"dhi":0,"dni":0,"ghi":0,"ozone":304,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":74,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":47.1,"timestamp_local":"2025-11-13T01:00:00","timestamp_utc":"2025-11-13T06:00:00","ts":1763013600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":260,"wind_gust_spd":10.1,"wind_spd":4.5},{"app_temp":46.2,"clouds":11,"clouds_hi":43,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:07","dewpt":39,"dhi":0,"dni":0,"ghi":0,"ozone":303,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":76,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":46.2,"timestamp_local":"2025-11-13T02:00:00","timestamp_utc":"2025-11-13T07:00:00","ts":1763017200,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":266,"wind_gust_spd":8.2,"wind_spd":6.3},{"app_temp":45.5,"clouds":14,"clouds_hi":69,"clouds_low":0,"clouds_mid":1,"datetime":"2025-11-13:08","dewpt":39.4,"dhi":0,"dni":0,"ghi":0,"ozone":302,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":79,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":45.5,"timestamp_local":"2025-11-13T03:00:00","timestamp_utc":"2025-11-13T08:00:00","ts":1763020800,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":273,"wind_gust_spd":6.3,"wind_spd":8.1},{"app_temp":39.4,"clouds":17,"clouds_hi":75,"clouds_low":0,"clouds_mid":13,"datetime":"2025-11-13:09","dewpt":39.2,"dhi":0,"dni":0,"ghi":0,"ozone":298,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":81,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":44.6,"timestamp_local":"2025-11-13T04:00:00","timestamp_utc":"2025-11-13T09:00:00","ts":1763024400,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"W","wind_cdir_full":"west","wind_dir":280,"wind_gust_spd":4.5,"wind_spd":9.8},{"app_temp":39.6,"clouds":17,"clouds_hi":98,"clouds_low":0,"clouds_mid":81,"datetime":"2025-11-13:10","dewpt":39,"dhi":0,"dni":0,"ghi":0,"ozone":298,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":82,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":44.1,"timestamp_local":"2025-11-13T05:00:00","timestamp_utc":"2025-11-13T10:00:00","ts":1763028000,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":283,"wind_gust_spd":6,"wind_spd":8.1},{"app_temp":39.9,"clouds":18,"clouds_hi":100,"clouds_low":0,"clouds_mid":98,"datetime":"2025-11-13:11","dewpt":39,"dhi":0,"dni":0,"ghi":0,"ozone":298,"pod":"n","pop":0,"precip":0,"pres":1011,"rh":84,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":0,"temp":43.7,"timestamp_local":"2025-11-13T06:00:00","timestamp_utc":"2025-11-13T11:00:00","ts":1763031600,"uv":0,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02n","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":286,"wind_gust_spd":7.6,"wind_spd":6.3},{"app_temp":40.5,"clouds":18,"clouds_hi":97,"clouds_low":0,"clouds_mid":100,"datetime":"2025-11-13:12","dewpt":38.8,"dhi":16,"dni":93,"ghi":10,"ozone":298,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":85,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":26.682377,"temp":43.2,"timestamp_local":"2025-11-13T07:00:00","timestamp_utc":"2025-11-13T12:00:00","ts":1763035200,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":290,"wind_gust_spd":9.2,"wind_spd":4.5},{"app_temp":47.1,"clouds":16,"clouds_hi":65,"clouds_low":0,"clouds_mid":67,"datetime":"2025-11-13:13","dewpt":39.9,"dhi":61,"dni":544,"ghi":168,"ozone":297,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":76,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":167.33405,"temp":47.1,"timestamp_local":"2025-11-13T08:00:00","timestamp_utc":"2025-11-13T13:00:00","ts":1763038800,"uv":1,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":293,"wind_gust_spd":8.3,"wind_spd":7.3},{"app_temp":51.1,"clouds":13,"clouds_hi":32,"clouds_low":0,"clouds_mid":33,"datetime":"2025-11-13:14","dewpt":40.1,"dhi":82,"dni":712,"ghi":339,"ozone":296,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":66,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":338.73718,"temp":51.1,"timestamp_local":"2025-11-13T09:00:00","timestamp_utc":"2025-11-13T14:00:00","ts":1763042400,"uv":2,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":296,"wind_gust_spd":7.4,"wind_spd":10.1},{"app_temp":55,"clouds":11,"clouds_hi":0,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:15","dewpt":40.1,"dhi":95,"dni":794,"ghi":479,"ozone":295,"pod":"d","pop":0,"precip":0,"pres":1013,"rh":57,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":478.9126,"temp":55,"timestamp_local":"2025-11-13T10:00:00","timestamp_utc":"2025-11-13T15:00:00","ts":1763046000,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":300,"wind_gust_spd":6.5,"wind_spd":13},{"app_temp":57.2,"clouds":13,"clouds_hi":1,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:16","dewpt":39.7,"dhi":102,"dni":835,"ghi":569,"ozone":294,"pod":"d","pop":0,"precip":0,"pres":1012,"rh":52,"slp":1020,"snow":0,"snow_depth":0,"solar_rad":568.46545,"temp":57.2,"timestamp_local":"2025-11-13T11:00:00","timestamp_utc":"2025-11-13T16:00:00","ts":1763049600,"uv":3,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":296,"wind_gust_spd":9.5,"wind_spd":11.2},{"app_temp":59.2,"clouds":14,"clouds_hi":3,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:17","dewpt":39,"dhi":104,"dni":847,"ghi":598,"ozone":294,"pod":"d","pop":0,"precip":0,"pres":1011,"rh":47,"slp":1019,"snow":0,"snow_depth":0,"solar_rad":597.59155,"temp":59.2,"timestamp_local":"2025-11-13T12:00:00","timestamp_utc":"2025-11-13T17:00:00","ts":1763053200,"uv":4,"vis":14.9,"weather":{"description":"Few clouds","icon":"c02d","code":801},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":293,"wind_gust_spd":12.4,"wind_spd":9.4},{"app_temp":64,"clouds":1,"clouds_hi":4,"clouds_low":0,"clouds_mid":0,"datetime":"2025-11-13:18","dewpt":35.1,"dhi":102,"dni":833,"ghi":564,"ozone":294,"pod":"d","pop":0,"precip":0,"pres":1011,"rh":34,"slp":1018,"snow":0,"snow_depth":0,"solar_rad":564.2199,"temp":64,"timestamp_local":"2025-11-13T13:00:00","timestamp_utc":"2025-11-13T18:00:00","ts":1763056800,"uv":4,"vis":14.9,"weather":{"description":"Clear Sky","icon":"c01d","code":800},"wind_cdir":"WNW","wind_cdir_full":"west-northwest","wind_dir":295,"wind_gust_spd":17.7,"wind_spd":12.9}],"lat":35.5,"lon":-78.5,"state_code":"NC","timezone":"America/New_York"}}]}	0429f1a5-0399-4b6f-8c86-da542a52a5b9	0	wXJ6yePE9hpJPTta	{"templateCredsSetupCompleted":true}	\N	t
\.


--
-- Data for Name: workflow_history; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.workflow_history ("versionId", "workflowId", authors, "createdAt", "updatedAt", nodes, connections) FROM stdin;
\.


--
-- Data for Name: workflow_statistics; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.workflow_statistics (count, "latestEvent", name, "workflowId", "rootCount") FROM stdin;
1	2025-10-29 21:57:29.682+00	data_loaded	wXJ6yePE9hpJPTta	1
7	2025-11-08 19:18:31.055+00	manual_error	wXJ6yePE9hpJPTta	0
13	2025-11-08 19:31:56.1+00	manual_success	wXJ6yePE9hpJPTta	0
\.


--
-- Data for Name: workflows_tags; Type: TABLE DATA; Schema: public; Owner: openagile
--

COPY public.workflows_tags ("workflowId", "tagId") FROM stdin;
\.


--
-- Name: auth_provider_sync_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.auth_provider_sync_history_id_seq', 1, false);


--
-- Name: execution_annotations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.execution_annotations_id_seq', 1, false);


--
-- Name: execution_entity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.execution_entity_id_seq', 20, true);


--
-- Name: execution_metadata_temp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.execution_metadata_temp_id_seq', 1, false);


--
-- Name: insights_by_period_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.insights_by_period_id_seq', 1, false);


--
-- Name: insights_metadata_metaId_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public."insights_metadata_metaId_seq"', 1, false);


--
-- Name: insights_raw_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.insights_raw_id_seq', 1, false);


--
-- Name: migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openagile
--

SELECT pg_catalog.setval('public.migrations_id_seq', 102, true);


--
-- Name: test_run PK_011c050f566e9db509a0fadb9b9; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.test_run
    ADD CONSTRAINT "PK_011c050f566e9db509a0fadb9b9" PRIMARY KEY (id);


--
-- Name: installed_packages PK_08cc9197c39b028c1e9beca225940576fd1a5804; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.installed_packages
    ADD CONSTRAINT "PK_08cc9197c39b028c1e9beca225940576fd1a5804" PRIMARY KEY ("packageName");


--
-- Name: execution_metadata PK_17a0b6284f8d626aae88e1c16e4; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_metadata
    ADD CONSTRAINT "PK_17a0b6284f8d626aae88e1c16e4" PRIMARY KEY (id);


--
-- Name: project_relation PK_1caaa312a5d7184a003be0f0cb6; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.project_relation
    ADD CONSTRAINT "PK_1caaa312a5d7184a003be0f0cb6" PRIMARY KEY ("projectId", "userId");


--
-- Name: folder_tag PK_27e4e00852f6b06a925a4d83a3e; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder_tag
    ADD CONSTRAINT "PK_27e4e00852f6b06a925a4d83a3e" PRIMARY KEY ("folderId", "tagId");


--
-- Name: role PK_35c9b140caaf6da09cfabb0d675; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT "PK_35c9b140caaf6da09cfabb0d675" PRIMARY KEY (slug);


--
-- Name: project PK_4d68b1358bb5b766d3e78f32f57; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT "PK_4d68b1358bb5b766d3e78f32f57" PRIMARY KEY (id);


--
-- Name: invalid_auth_token PK_5779069b7235b256d91f7af1a15; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.invalid_auth_token
    ADD CONSTRAINT "PK_5779069b7235b256d91f7af1a15" PRIMARY KEY (token);


--
-- Name: shared_workflow PK_5ba87620386b847201c9531c58f; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_workflow
    ADD CONSTRAINT "PK_5ba87620386b847201c9531c58f" PRIMARY KEY ("workflowId", "projectId");


--
-- Name: folder PK_6278a41a706740c94c02e288df8; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder
    ADD CONSTRAINT "PK_6278a41a706740c94c02e288df8" PRIMARY KEY (id);


--
-- Name: data_table_column PK_673cb121ee4a8a5e27850c72c51; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table_column
    ADD CONSTRAINT "PK_673cb121ee4a8a5e27850c72c51" PRIMARY KEY (id);


--
-- Name: annotation_tag_entity PK_69dfa041592c30bbc0d4b84aa00; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.annotation_tag_entity
    ADD CONSTRAINT "PK_69dfa041592c30bbc0d4b84aa00" PRIMARY KEY (id);


--
-- Name: execution_annotations PK_7afcf93ffa20c4252869a7c6a23; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotations
    ADD CONSTRAINT "PK_7afcf93ffa20c4252869a7c6a23" PRIMARY KEY (id);


--
-- Name: migrations PK_8c82d7f526340ab734260ea46be; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.migrations
    ADD CONSTRAINT "PK_8c82d7f526340ab734260ea46be" PRIMARY KEY (id);


--
-- Name: installed_nodes PK_8ebd28194e4f792f96b5933423fc439df97d9689; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.installed_nodes
    ADD CONSTRAINT "PK_8ebd28194e4f792f96b5933423fc439df97d9689" PRIMARY KEY (name);


--
-- Name: shared_credentials PK_8ef3a59796a228913f251779cff; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_credentials
    ADD CONSTRAINT "PK_8ef3a59796a228913f251779cff" PRIMARY KEY ("credentialsId", "projectId");


--
-- Name: test_case_execution PK_90c121f77a78a6580e94b794bce; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.test_case_execution
    ADD CONSTRAINT "PK_90c121f77a78a6580e94b794bce" PRIMARY KEY (id);


--
-- Name: user_api_keys PK_978fa5caa3468f463dac9d92e69; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.user_api_keys
    ADD CONSTRAINT "PK_978fa5caa3468f463dac9d92e69" PRIMARY KEY (id);


--
-- Name: execution_annotation_tags PK_979ec03d31294cca484be65d11f; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotation_tags
    ADD CONSTRAINT "PK_979ec03d31294cca484be65d11f" PRIMARY KEY ("annotationId", "tagId");


--
-- Name: webhook_entity PK_b21ace2e13596ccd87dc9bf4ea6; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.webhook_entity
    ADD CONSTRAINT "PK_b21ace2e13596ccd87dc9bf4ea6" PRIMARY KEY ("webhookPath", method);


--
-- Name: insights_by_period PK_b606942249b90cc39b0265f0575; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_by_period
    ADD CONSTRAINT "PK_b606942249b90cc39b0265f0575" PRIMARY KEY (id);


--
-- Name: workflow_history PK_b6572dd6173e4cd06fe79937b58; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_history
    ADD CONSTRAINT "PK_b6572dd6173e4cd06fe79937b58" PRIMARY KEY ("versionId");


--
-- Name: scope PK_bfc45df0481abd7f355d6187da1; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.scope
    ADD CONSTRAINT "PK_bfc45df0481abd7f355d6187da1" PRIMARY KEY (slug);


--
-- Name: processed_data PK_ca04b9d8dc72de268fe07a65773; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.processed_data
    ADD CONSTRAINT "PK_ca04b9d8dc72de268fe07a65773" PRIMARY KEY ("workflowId", context);


--
-- Name: settings PK_dc0fe14e6d9943f268e7b119f69ab8bd; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT "PK_dc0fe14e6d9943f268e7b119f69ab8bd" PRIMARY KEY (key);


--
-- Name: data_table PK_e226d0001b9e6097cbfe70617cb; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table
    ADD CONSTRAINT "PK_e226d0001b9e6097cbfe70617cb" PRIMARY KEY (id);


--
-- Name: user PK_ea8f538c94b6e352418254ed6474a81f; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "PK_ea8f538c94b6e352418254ed6474a81f" PRIMARY KEY (id);


--
-- Name: insights_raw PK_ec15125755151e3a7e00e00014f; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_raw
    ADD CONSTRAINT "PK_ec15125755151e3a7e00e00014f" PRIMARY KEY (id);


--
-- Name: insights_metadata PK_f448a94c35218b6208ce20cf5a1; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_metadata
    ADD CONSTRAINT "PK_f448a94c35218b6208ce20cf5a1" PRIMARY KEY ("metaId");


--
-- Name: role_scope PK_role_scope; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.role_scope
    ADD CONSTRAINT "PK_role_scope" PRIMARY KEY ("roleSlug", "scopeSlug");


--
-- Name: data_table_column UQ_8082ec4890f892f0bc77473a123; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table_column
    ADD CONSTRAINT "UQ_8082ec4890f892f0bc77473a123" UNIQUE ("dataTableId", name);


--
-- Name: data_table UQ_b23096ef747281ac944d28e8b0d; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table
    ADD CONSTRAINT "UQ_b23096ef747281ac944d28e8b0d" UNIQUE ("projectId", name);


--
-- Name: user UQ_e12875dfb3b1d92d7d7c5377e2; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "UQ_e12875dfb3b1d92d7d7c5377e2" UNIQUE (email);


--
-- Name: auth_identity auth_identity_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.auth_identity
    ADD CONSTRAINT auth_identity_pkey PRIMARY KEY ("providerId", "providerType");


--
-- Name: auth_provider_sync_history auth_provider_sync_history_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.auth_provider_sync_history
    ADD CONSTRAINT auth_provider_sync_history_pkey PRIMARY KEY (id);


--
-- Name: credentials_entity credentials_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.credentials_entity
    ADD CONSTRAINT credentials_entity_pkey PRIMARY KEY (id);


--
-- Name: event_destinations event_destinations_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.event_destinations
    ADD CONSTRAINT event_destinations_pkey PRIMARY KEY (id);


--
-- Name: execution_data execution_data_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_data
    ADD CONSTRAINT execution_data_pkey PRIMARY KEY ("executionId");


--
-- Name: execution_entity pk_e3e63bbf986767844bbe1166d4e; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_entity
    ADD CONSTRAINT pk_e3e63bbf986767844bbe1166d4e PRIMARY KEY (id);


--
-- Name: workflow_statistics pk_workflow_statistics; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_statistics
    ADD CONSTRAINT pk_workflow_statistics PRIMARY KEY ("workflowId", name);


--
-- Name: workflows_tags pk_workflows_tags; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflows_tags
    ADD CONSTRAINT pk_workflows_tags PRIMARY KEY ("workflowId", "tagId");


--
-- Name: tag_entity tag_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.tag_entity
    ADD CONSTRAINT tag_entity_pkey PRIMARY KEY (id);


--
-- Name: variables variables_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.variables
    ADD CONSTRAINT variables_pkey PRIMARY KEY (id);


--
-- Name: workflow_entity workflow_entity_pkey; Type: CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_entity
    ADD CONSTRAINT workflow_entity_pkey PRIMARY KEY (id);


--
-- Name: IDX_14f68deffaf858465715995508; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_14f68deffaf858465715995508" ON public.folder USING btree ("projectId", id);


--
-- Name: IDX_1d8ab99d5861c9388d2dc1cf73; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_1d8ab99d5861c9388d2dc1cf73" ON public.insights_metadata USING btree ("workflowId");


--
-- Name: IDX_1e31657f5fe46816c34be7c1b4; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_1e31657f5fe46816c34be7c1b4" ON public.workflow_history USING btree ("workflowId");


--
-- Name: IDX_1ef35bac35d20bdae979d917a3; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_1ef35bac35d20bdae979d917a3" ON public.user_api_keys USING btree ("apiKey");


--
-- Name: IDX_5f0643f6717905a05164090dde; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_5f0643f6717905a05164090dde" ON public.project_relation USING btree ("userId");


--
-- Name: IDX_60b6a84299eeb3f671dfec7693; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_60b6a84299eeb3f671dfec7693" ON public.insights_by_period USING btree ("periodStart", type, "periodUnit", "metaId");


--
-- Name: IDX_61448d56d61802b5dfde5cdb00; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_61448d56d61802b5dfde5cdb00" ON public.project_relation USING btree ("projectId");


--
-- Name: IDX_63d7bbae72c767cf162d459fcc; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_63d7bbae72c767cf162d459fcc" ON public.user_api_keys USING btree ("userId", label);


--
-- Name: IDX_8e4b4774db42f1e6dda3452b2a; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_8e4b4774db42f1e6dda3452b2a" ON public.test_case_execution USING btree ("testRunId");


--
-- Name: IDX_97f863fa83c4786f1956508496; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_97f863fa83c4786f1956508496" ON public.execution_annotations USING btree ("executionId");


--
-- Name: IDX_a3697779b366e131b2bbdae297; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_a3697779b366e131b2bbdae297" ON public.execution_annotation_tags USING btree ("tagId");


--
-- Name: IDX_ae51b54c4bb430cf92f48b623f; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_ae51b54c4bb430cf92f48b623f" ON public.annotation_tag_entity USING btree (name);


--
-- Name: IDX_c1519757391996eb06064f0e7c; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_c1519757391996eb06064f0e7c" ON public.execution_annotation_tags USING btree ("annotationId");


--
-- Name: IDX_cec8eea3bf49551482ccb4933e; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX "IDX_cec8eea3bf49551482ccb4933e" ON public.execution_metadata USING btree ("executionId", key);


--
-- Name: IDX_d6870d3b6e4c185d33926f423c; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_d6870d3b6e4c185d33926f423c" ON public.test_run USING btree ("workflowId");


--
-- Name: IDX_execution_entity_deletedAt; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_execution_entity_deletedAt" ON public.execution_entity USING btree ("deletedAt");


--
-- Name: IDX_role_scope_scopeSlug; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_role_scope_scopeSlug" ON public.role_scope USING btree ("scopeSlug");


--
-- Name: IDX_workflow_entity_name; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX "IDX_workflow_entity_name" ON public.workflow_entity USING btree (name);


--
-- Name: idx_07fde106c0b471d8cc80a64fc8; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_07fde106c0b471d8cc80a64fc8 ON public.credentials_entity USING btree (type);


--
-- Name: idx_16f4436789e804e3e1c9eeb240; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_16f4436789e804e3e1c9eeb240 ON public.webhook_entity USING btree ("webhookId", method, "pathLength");


--
-- Name: idx_812eb05f7451ca757fb98444ce; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX idx_812eb05f7451ca757fb98444ce ON public.tag_entity USING btree (name);


--
-- Name: idx_execution_entity_stopped_at_status_deleted_at; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_execution_entity_stopped_at_status_deleted_at ON public.execution_entity USING btree ("stoppedAt", status, "deletedAt") WHERE (("stoppedAt" IS NOT NULL) AND ("deletedAt" IS NULL));


--
-- Name: idx_execution_entity_wait_till_status_deleted_at; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_execution_entity_wait_till_status_deleted_at ON public.execution_entity USING btree ("waitTill", status, "deletedAt") WHERE (("waitTill" IS NOT NULL) AND ("deletedAt" IS NULL));


--
-- Name: idx_execution_entity_workflow_id_started_at; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_execution_entity_workflow_id_started_at ON public.execution_entity USING btree ("workflowId", "startedAt") WHERE (("startedAt" IS NOT NULL) AND ("deletedAt" IS NULL));


--
-- Name: idx_workflows_tags_workflow_id; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX idx_workflows_tags_workflow_id ON public.workflows_tags USING btree ("workflowId");


--
-- Name: pk_credentials_entity_id; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX pk_credentials_entity_id ON public.credentials_entity USING btree (id);


--
-- Name: pk_tag_entity_id; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX pk_tag_entity_id ON public.tag_entity USING btree (id);


--
-- Name: pk_workflow_entity_id; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX pk_workflow_entity_id ON public.workflow_entity USING btree (id);


--
-- Name: project_relation_role_idx; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX project_relation_role_idx ON public.project_relation USING btree (role);


--
-- Name: project_relation_role_project_idx; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX project_relation_role_project_idx ON public.project_relation USING btree ("projectId", role);


--
-- Name: user_role_idx; Type: INDEX; Schema: public; Owner: openagile
--

CREATE INDEX user_role_idx ON public."user" USING btree ("roleSlug");


--
-- Name: variables_global_key_unique; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX variables_global_key_unique ON public.variables USING btree (key) WHERE ("projectId" IS NULL);


--
-- Name: variables_project_key_unique; Type: INDEX; Schema: public; Owner: openagile
--

CREATE UNIQUE INDEX variables_project_key_unique ON public.variables USING btree ("projectId", key) WHERE ("projectId" IS NOT NULL);


--
-- Name: processed_data FK_06a69a7032c97a763c2c7599464; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.processed_data
    ADD CONSTRAINT "FK_06a69a7032c97a763c2c7599464" FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: insights_metadata FK_1d8ab99d5861c9388d2dc1cf733; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_metadata
    ADD CONSTRAINT "FK_1d8ab99d5861c9388d2dc1cf733" FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE SET NULL;


--
-- Name: workflow_history FK_1e31657f5fe46816c34be7c1b4b; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_history
    ADD CONSTRAINT "FK_1e31657f5fe46816c34be7c1b4b" FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: insights_metadata FK_2375a1eda085adb16b24615b69c; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_metadata
    ADD CONSTRAINT "FK_2375a1eda085adb16b24615b69c" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE SET NULL;


--
-- Name: execution_metadata FK_31d0b4c93fb85ced26f6005cda3; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_metadata
    ADD CONSTRAINT "FK_31d0b4c93fb85ced26f6005cda3" FOREIGN KEY ("executionId") REFERENCES public.execution_entity(id) ON DELETE CASCADE;


--
-- Name: shared_credentials FK_416f66fc846c7c442970c094ccf; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_credentials
    ADD CONSTRAINT "FK_416f66fc846c7c442970c094ccf" FOREIGN KEY ("credentialsId") REFERENCES public.credentials_entity(id) ON DELETE CASCADE;


--
-- Name: variables FK_42f6c766f9f9d2edcc15bdd6e9b; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.variables
    ADD CONSTRAINT "FK_42f6c766f9f9d2edcc15bdd6e9b" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: project_relation FK_5f0643f6717905a05164090dde7; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.project_relation
    ADD CONSTRAINT "FK_5f0643f6717905a05164090dde7" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: project_relation FK_61448d56d61802b5dfde5cdb002; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.project_relation
    ADD CONSTRAINT "FK_61448d56d61802b5dfde5cdb002" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: insights_by_period FK_6414cfed98daabbfdd61a1cfbc0; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_by_period
    ADD CONSTRAINT "FK_6414cfed98daabbfdd61a1cfbc0" FOREIGN KEY ("metaId") REFERENCES public.insights_metadata("metaId") ON DELETE CASCADE;


--
-- Name: insights_raw FK_6e2e33741adef2a7c5d66befa4e; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.insights_raw
    ADD CONSTRAINT "FK_6e2e33741adef2a7c5d66befa4e" FOREIGN KEY ("metaId") REFERENCES public.insights_metadata("metaId") ON DELETE CASCADE;


--
-- Name: installed_nodes FK_73f857fc5dce682cef8a99c11dbddbc969618951; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.installed_nodes
    ADD CONSTRAINT "FK_73f857fc5dce682cef8a99c11dbddbc969618951" FOREIGN KEY (package) REFERENCES public.installed_packages("packageName") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: folder FK_804ea52f6729e3940498bd54d78; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder
    ADD CONSTRAINT "FK_804ea52f6729e3940498bd54d78" FOREIGN KEY ("parentFolderId") REFERENCES public.folder(id) ON DELETE CASCADE;


--
-- Name: shared_credentials FK_812c2852270da1247756e77f5a4; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_credentials
    ADD CONSTRAINT "FK_812c2852270da1247756e77f5a4" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: test_case_execution FK_8e4b4774db42f1e6dda3452b2af; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.test_case_execution
    ADD CONSTRAINT "FK_8e4b4774db42f1e6dda3452b2af" FOREIGN KEY ("testRunId") REFERENCES public.test_run(id) ON DELETE CASCADE;


--
-- Name: data_table_column FK_930b6e8faaf88294cef23484160; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table_column
    ADD CONSTRAINT "FK_930b6e8faaf88294cef23484160" FOREIGN KEY ("dataTableId") REFERENCES public.data_table(id) ON DELETE CASCADE;


--
-- Name: folder_tag FK_94a60854e06f2897b2e0d39edba; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder_tag
    ADD CONSTRAINT "FK_94a60854e06f2897b2e0d39edba" FOREIGN KEY ("folderId") REFERENCES public.folder(id) ON DELETE CASCADE;


--
-- Name: execution_annotations FK_97f863fa83c4786f19565084960; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotations
    ADD CONSTRAINT "FK_97f863fa83c4786f19565084960" FOREIGN KEY ("executionId") REFERENCES public.execution_entity(id) ON DELETE CASCADE;


--
-- Name: execution_annotation_tags FK_a3697779b366e131b2bbdae2976; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotation_tags
    ADD CONSTRAINT "FK_a3697779b366e131b2bbdae2976" FOREIGN KEY ("tagId") REFERENCES public.annotation_tag_entity(id) ON DELETE CASCADE;


--
-- Name: shared_workflow FK_a45ea5f27bcfdc21af9b4188560; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_workflow
    ADD CONSTRAINT "FK_a45ea5f27bcfdc21af9b4188560" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: folder FK_a8260b0b36939c6247f385b8221; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder
    ADD CONSTRAINT "FK_a8260b0b36939c6247f385b8221" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: execution_annotation_tags FK_c1519757391996eb06064f0e7c8; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_annotation_tags
    ADD CONSTRAINT "FK_c1519757391996eb06064f0e7c8" FOREIGN KEY ("annotationId") REFERENCES public.execution_annotations(id) ON DELETE CASCADE;


--
-- Name: data_table FK_c2a794257dee48af7c9abf681de; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.data_table
    ADD CONSTRAINT "FK_c2a794257dee48af7c9abf681de" FOREIGN KEY ("projectId") REFERENCES public.project(id) ON DELETE CASCADE;


--
-- Name: project_relation FK_c6b99592dc96b0d836d7a21db91; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.project_relation
    ADD CONSTRAINT "FK_c6b99592dc96b0d836d7a21db91" FOREIGN KEY (role) REFERENCES public.role(slug);


--
-- Name: test_run FK_d6870d3b6e4c185d33926f423c8; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.test_run
    ADD CONSTRAINT "FK_d6870d3b6e4c185d33926f423c8" FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: shared_workflow FK_daa206a04983d47d0a9c34649ce; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.shared_workflow
    ADD CONSTRAINT "FK_daa206a04983d47d0a9c34649ce" FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: folder_tag FK_dc88164176283de80af47621746; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.folder_tag
    ADD CONSTRAINT "FK_dc88164176283de80af47621746" FOREIGN KEY ("tagId") REFERENCES public.tag_entity(id) ON DELETE CASCADE;


--
-- Name: user_api_keys FK_e131705cbbc8fb589889b02d457; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.user_api_keys
    ADD CONSTRAINT "FK_e131705cbbc8fb589889b02d457" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: test_case_execution FK_e48965fac35d0f5b9e7f51d8c44; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.test_case_execution
    ADD CONSTRAINT "FK_e48965fac35d0f5b9e7f51d8c44" FOREIGN KEY ("executionId") REFERENCES public.execution_entity(id) ON DELETE SET NULL;


--
-- Name: user FK_eaea92ee7bfb9c1b6cd01505d56; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "FK_eaea92ee7bfb9c1b6cd01505d56" FOREIGN KEY ("roleSlug") REFERENCES public.role(slug);


--
-- Name: role_scope FK_role; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.role_scope
    ADD CONSTRAINT "FK_role" FOREIGN KEY ("roleSlug") REFERENCES public.role(slug) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_scope FK_scope; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.role_scope
    ADD CONSTRAINT "FK_scope" FOREIGN KEY ("scopeSlug") REFERENCES public.scope(slug) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: auth_identity auth_identity_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.auth_identity
    ADD CONSTRAINT "auth_identity_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: execution_data execution_data_fk; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_data
    ADD CONSTRAINT execution_data_fk FOREIGN KEY ("executionId") REFERENCES public.execution_entity(id) ON DELETE CASCADE;


--
-- Name: execution_entity fk_execution_entity_workflow_id; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.execution_entity
    ADD CONSTRAINT fk_execution_entity_workflow_id FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: webhook_entity fk_webhook_entity_workflow_id; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.webhook_entity
    ADD CONSTRAINT fk_webhook_entity_workflow_id FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: workflow_entity fk_workflow_parent_folder; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_entity
    ADD CONSTRAINT fk_workflow_parent_folder FOREIGN KEY ("parentFolderId") REFERENCES public.folder(id) ON DELETE CASCADE;


--
-- Name: workflow_statistics fk_workflow_statistics_workflow_id; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflow_statistics
    ADD CONSTRAINT fk_workflow_statistics_workflow_id FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- Name: workflows_tags fk_workflows_tags_tag_id; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflows_tags
    ADD CONSTRAINT fk_workflows_tags_tag_id FOREIGN KEY ("tagId") REFERENCES public.tag_entity(id) ON DELETE CASCADE;


--
-- Name: workflows_tags fk_workflows_tags_workflow_id; Type: FK CONSTRAINT; Schema: public; Owner: openagile
--

ALTER TABLE ONLY public.workflows_tags
    ADD CONSTRAINT fk_workflows_tags_workflow_id FOREIGN KEY ("workflowId") REFERENCES public.workflow_entity(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict wy8XUyO9pjeALOqStbzVMlS54DMDCgh8fHtaMrR1W4oXA3NaP8zXdMl87oB4RaH


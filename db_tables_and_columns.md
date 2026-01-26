# DB / Tables / Columns Inventory

This repository uses a PostgreSQL database (default `DB_NAME=jobmatch` in `backend/.env`).

Total tables found: **27**

## personal_date

| Column | Definition | References |
|---|---|---|
| `user_id` | SERIAL PRIMARY KEY |  |
| `name` | VARCHAR(100) NOT NULL |  |
| `email` | VARCHAR(255) UNIQUE NOT NULL |  |
| `password` | VARCHAR(255) NOT NULL |  |
| `age` | INTEGER |  |
| `gender` | VARCHAR(20) |  |
| `phone` | VARCHAR(20) |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## company_date

| Column | Definition | References |
|---|---|---|
| `company_id` | UUID PRIMARY KEY DEFAULT gen_random_uuid() |  |
| `company_name` | VARCHAR(255) NOT NULL |  |
| `email` | VARCHAR(255) UNIQUE NOT NULL |  |
| `password` | VARCHAR(255) NOT NULL |  |
| `industry` | VARCHAR(100) |  |
| `company_size` | VARCHAR(50) |  |
| `founded_year` | INTEGER |  |
| `website_url` | VARCHAR(500) |  |
| `description` | TEXT |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## conversation_turns

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER NOT NULL |  |
| `session_id` | VARCHAR(100) NOT NULL |  |
| `turn_number` | INTEGER NOT NULL |  |
| `user_message` | TEXT |  |
| `bot_message` | TEXT |  |
| `extracted_info` | JSONB |  |
| `top_score` | FLOAT |  |
| `top_match_percentage` | FLOAT |  |
| `candidate_count` | INTEGER |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## user_insights

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER NOT NULL |  |
| `session_id` | VARCHAR(100) NOT NULL |  |
| `insights` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

**Table constraints**

- UNIQUE(user_id, session_id)

## score_history

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER NOT NULL |  |
| `session_id` | VARCHAR(100) NOT NULL |  |
| `turn_number` | INTEGER NOT NULL |  |
| `job_id` | VARCHAR(100) NOT NULL |  |
| `score` | FLOAT |  |
| `match_percentage` | FLOAT |  |
| `score_details` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## chat_history

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER NOT NULL |  |
| `session_id` | VARCHAR(100) NOT NULL |  |
| `sender` | VARCHAR(10) NOT NULL |  |
| `message` | TEXT NOT NULL |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## global_preference_trends

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `preference_key` | VARCHAR(100) NOT NULL |  |
| `preference_value` | TEXT |  |
| `occurrence_count` | INTEGER DEFAULT 1 |  |
| `unique_users` | INTEGER DEFAULT 1 |  |
| `last_detected` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `trend_score` | FLOAT |  |
| `category` | VARCHAR(50) |  |

**Table constraints**

- UNIQUE(preference_key, preference_value)

## trend_thresholds

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `threshold_name` | VARCHAR(100) UNIQUE NOT NULL |  |
| `threshold_value` | INTEGER NOT NULL |  |
| `description` | TEXT |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## current_weekly_trends

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `week_start` | DATE NOT NULL |  |
| `trend_data` | JSONB NOT NULL |  |
| `generated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

**Table constraints**

- UNIQUE(week_start)

## baseline_job_fields

| Column | Definition | References |
|---|---|---|
| `field_id` | SERIAL PRIMARY KEY |  |
| `field_name` | VARCHAR(100) UNIQUE NOT NULL |  |
| `field_type` | VARCHAR(50) NOT NULL |  |
| `label` | VARCHAR(200) NOT NULL |  |
| `question_template` | TEXT |  |
| `options` | JSONB |  |
| `placeholder` | TEXT |  |
| `required` | BOOLEAN DEFAULT FALSE |  |
| `priority` | INTEGER DEFAULT 0 |  |
| `category` | VARCHAR(50) |  |
| `promoted_at` | TIMESTAMP |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## dynamic_questions

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `question_text` | TEXT NOT NULL |  |
| `question_type` | VARCHAR(50) |  |
| `target_context` | VARCHAR(100) |  |
| `options` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## chat_sessions

| Column | Definition | References |
|---|---|---|
| `session_id` | VARCHAR(255) PRIMARY KEY |  |
| `user_id` | VARCHAR(255) NOT NULL |  |
| `session_data` | JSONB NOT NULL |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## user_profile

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `job_title` | VARCHAR(200) |  |
| `years_of_experience` | INTEGER |  |
| `skills` | TEXT[] |  |
| `education_level` | VARCHAR(50) |  |
| `location_prefecture` | VARCHAR(50) |  |
| `location_city` | VARCHAR(100) |  |
| `salary_min` | INTEGER |  |
| `salary_max` | INTEGER |  |
| `work_style_preference` | TEXT |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

**Table constraints**

- UNIQUE(user_id)

## user_preferences_profile

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `job_title` | VARCHAR(200) |  |
| `location_prefecture` | VARCHAR(50) |  |
| `location_city` | VARCHAR(100) |  |
| `salary_min` | INTEGER |  |
| `salary_max` | INTEGER |  |
| `remote_work_preference` | VARCHAR(50) |  |
| `employment_type` | VARCHAR(50) |  |
| `industry_preferences` | TEXT[] |  |
| `work_hours_preference` | VARCHAR(100) |  |
| `company_size_preference` | VARCHAR(50) |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

**Table constraints**

- UNIQUE(user_id)

## user_personality_analysis

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `personality_traits` | JSONB |  |
| `work_values` | JSONB |  |
| `communication_style` | VARCHAR(50) |  |
| `decision_making_style` | VARCHAR(50) |  |
| `analyzed_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

**Table constraints**

- UNIQUE(user_id)

## user_sessions

| Column | Definition | References |
|---|---|---|
| `session_id` | VARCHAR(255) PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `session_data` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `expires_at` | TIMESTAMP |  |

## conversation_logs

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `session_id` | VARCHAR(100) NOT NULL |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `turn_number` | INTEGER NOT NULL |  |
| `user_message` | TEXT |  |
| `ai_response` | TEXT |  |
| `extracted_intent` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## conversation_sessions

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `session_id` | VARCHAR(100) NOT NULL UNIQUE |  |
| `total_turns` | INTEGER |  |
| `end_reason` | VARCHAR(50) |  |
| `final_match_percentage` | FLOAT |  |
| `presented_jobs` | JSONB |  |
| `started_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `ended_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## search_history

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `search_query` | TEXT |  |
| `filters` | JSONB |  |
| `results_count` | INTEGER |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## company_profile

| Column | Definition | References |
|---|---|---|
| `id` | UUID PRIMARY KEY DEFAULT gen_random_uuid() |  |
| `company_id` | UUID REFERENCES company_date(company_id) ON DELETE CASCADE | company_date(company_id) |
| `job_title` | VARCHAR(200) NOT NULL |  |
| `job_description` | TEXT NOT NULL |  |
| `location_prefecture` | VARCHAR(50) NOT NULL |  |
| `location_city` | VARCHAR(100) |  |
| `salary_min` | INTEGER NOT NULL |  |
| `salary_max` | INTEGER NOT NULL |  |
| `employment_type` | VARCHAR(50) DEFAULT '正社員' |  |
| `remote_option` | VARCHAR(50) |  |
| `flex_time` | BOOLEAN DEFAULT FALSE |  |
| `latest_start_time` | TIME |  |
| `side_job_allowed` | BOOLEAN DEFAULT FALSE |  |
| `team_size` | VARCHAR(50) |  |
| `development_method` | VARCHAR(100) |  |
| `tech_stack` | JSONB |  |
| `required_skills` | TEXT[] |  |
| `preferred_skills` | TEXT[] |  |
| `benefits` | TEXT[] |  |
| `work_style_details` | TEXT |  |
| `team_culture_details` | TEXT |  |
| `growth_opportunities_details` | TEXT |  |
| `benefits_details` | TEXT |  |
| `office_environment_details` | TEXT |  |
| `project_details` | TEXT |  |
| `company_appeal_text` | TEXT |  |
| `ai_extracted_features` | JSONB |  |
| `additional_questions` | JSONB |  |
| `embedding` | VECTOR(1536) |  |
| `status` | VARCHAR(20) DEFAULT 'active' |  |
| `view_count` | INTEGER DEFAULT 0 |  |
| `click_count` | INTEGER DEFAULT 0 |  |
| `favorite_count` | INTEGER DEFAULT 0 |  |
| `apply_count` | INTEGER DEFAULT 0 |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `updated_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## user_question_responses

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `question_id` | INTEGER REFERENCES dynamic_questions(id) ON DELETE CASCADE | dynamic_questions(id) |
| `response_text` | TEXT |  |
| `response_data` | JSONB |  |
| `session_id` | VARCHAR(100) |  |
| `answered_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## job_attributes

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `attribute_name` | VARCHAR(100) NOT NULL |  |
| `attribute_value` | TEXT |  |
| `attribute_type` | VARCHAR(50) |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## job_additional_answers

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `question_text` | TEXT NOT NULL |  |
| `answer_text` | TEXT |  |
| `question_order` | INTEGER |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## user_interactions

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `interaction_type` | VARCHAR(50) NOT NULL |  |
| `session_id` | VARCHAR(100) |  |
| `interaction_data` | JSONB |  |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## missing_job_info_log

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE SET NULL | personal_date(user_id) |
| `missing_field` | VARCHAR(100) NOT NULL |  |
| `detected_from` | VARCHAR(50) |  |
| `detected_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |

## company_enrichment_requests

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `company_id` | UUID REFERENCES company_date(company_id) ON DELETE CASCADE | company_date(company_id) |
| `missing_field` | VARCHAR(100) NOT NULL |  |
| `question_text` | TEXT NOT NULL |  |
| `question_type` | VARCHAR(50) |  |
| `priority_score` | INTEGER |  |
| `detection_count` | INTEGER DEFAULT 1 |  |
| `status` | VARCHAR(50) DEFAULT 'pending' |  |
| `requested_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `responded_at` | TIMESTAMP |  |
| `response_text` | TEXT |  |

## scout_messages

| Column | Definition | References |
|---|---|---|
| `id` | SERIAL PRIMARY KEY |  |
| `company_id` | UUID REFERENCES company_date(company_id) ON DELETE CASCADE | company_date(company_id) |
| `job_id` | UUID REFERENCES company_profile(id) ON DELETE CASCADE | company_profile(id) |
| `user_id` | INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE | personal_date(user_id) |
| `message_title` | VARCHAR(255) NOT NULL |  |
| `message_body` | TEXT NOT NULL |  |
| `match_score` | FLOAT |  |
| `match_reasons` | JSONB |  |
| `status` | VARCHAR(50) DEFAULT 'sent' |  |
| `sent_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP |  |
| `read_at` | TIMESTAMP |  |
| `replied_at` | TIMESTAMP |  |


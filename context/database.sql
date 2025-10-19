-- esquema inicial para buzon_quejas
-- DB: compatible con PostgreSQL (ajustar tipos para MySQL si se prefiere)

-- habilitar extensión para generación de UUID (pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Función: trigger para actualizar campo updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
	NEW.updated_at = now();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tabla: rutas de camiones
CREATE TABLE IF NOT EXISTS routes (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	name VARCHAR(255) NOT NULL,
	metadata JSONB,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla: unidades (vehicles / unidades de transporte)
CREATE TABLE IF NOT EXISTS units (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	unit_number VARCHAR(32) NOT NULL UNIQUE,
	route_id UUID REFERENCES routes(id) ON DELETE SET NULL,
	metadata JSONB,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla: preguntas de la encuesta
CREATE TABLE IF NOT EXISTS questions (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	text TEXT NOT NULL,
	type VARCHAR(32) NOT NULL, -- 'rating' | 'text' | 'choice' | 'multi_choice'
	required BOOLEAN DEFAULT true,
	position INT DEFAULT 0,
	active BOOLEAN DEFAULT true,
	metadata JSONB,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Opciones para preguntas tipo choice / multi_choice
CREATE TABLE IF NOT EXISTS question_options (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
	value VARCHAR(255) NOT NULL,
	label VARCHAR(255) NOT NULL,
	position INT DEFAULT 0,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Encuestas enviadas / reportes (cada envío corresponde a una survey_record)
CREATE TABLE IF NOT EXISTS survey_submissions (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
	submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	metadata JSONB,
	user_agent TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Respuestas individuales asociadas a una submission y a una pregunta
CREATE TABLE IF NOT EXISTS answers (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	submission_id UUID NOT NULL REFERENCES survey_submissions(id) ON DELETE CASCADE,
	question_id UUID NOT NULL REFERENCES questions(id) ON DELETE SET NULL,
	-- Dependiendo del tipo, store raw_value and typed columns
	raw_value TEXT,
	numeric_value NUMERIC,
	option_id UUID REFERENCES question_options(id) ON DELETE SET NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla: motivos de queja
CREATE TABLE IF NOT EXISTS complaint_reasons (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	code VARCHAR(64) NOT NULL UNIQUE,
	label VARCHAR(255) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla: quejas
CREATE TABLE IF NOT EXISTS complaints (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
	reason_id UUID REFERENCES complaint_reasons(id) ON DELETE SET NULL,
	text TEXT NOT NULL,
	submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	metadata JSONB,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_survey_submissions_unit_id ON survey_submissions(unit_id);
CREATE INDEX IF NOT EXISTS idx_survey_submissions_submitted_at ON survey_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_questions_active_position ON questions(active, position);

-- Triggers para actualizar updated_at en tablas relevantes
DROP TRIGGER IF EXISTS set_timestamp ON units;
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON units
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_q ON questions;
CREATE TRIGGER set_timestamp_q
BEFORE UPDATE ON questions
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_routes ON routes;
CREATE TRIGGER set_timestamp_routes
BEFORE UPDATE ON routes
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_qopts ON question_options;
CREATE TRIGGER set_timestamp_qopts
BEFORE UPDATE ON question_options
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_complaint_reasons ON complaint_reasons;
CREATE TRIGGER set_timestamp_complaint_reasons
BEFORE UPDATE ON complaint_reasons
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_complaints ON complaints;
CREATE TRIGGER set_timestamp_complaints
BEFORE UPDATE ON complaints
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

DROP TRIGGER IF EXISTS set_timestamp_answers ON answers;
CREATE TRIGGER set_timestamp_answers
BEFORE UPDATE ON answers
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Seeds mínimos (opcional)
-- INSERT mínima: usar la columna correcta `unit_number`.
INSERT INTO units (unit_number) VALUES ('82') ON CONFLICT (unit_number) DO NOTHING;


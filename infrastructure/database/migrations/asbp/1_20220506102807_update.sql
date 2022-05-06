-- upgrade --
ALTER TABLE "claim" ALTER COLUMN "pass_type" TYPE VARCHAR(24) USING "pass_type"::VARCHAR(24);
-- downgrade --
ALTER TABLE "claim" ALTER COLUMN "pass_type" TYPE VARCHAR(24) USING "pass_type"::VARCHAR(24);

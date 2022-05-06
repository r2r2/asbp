-- upgrade --
CREATE TABLE IF NOT EXISTS "claimway" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "claimway" IS 'Маршрут согласования заявки';
CREATE TABLE IF NOT EXISTS "drivelicense" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "date_of_issue" TIMESTAMPTZ,
    "expiration_date" TIMESTAMPTZ,
    "place_of_issue" VARCHAR(64),
    "address_of_issue" VARCHAR(64),
    "number" BIGINT NOT NULL UNIQUE,
    "categories" VARCHAR(16)
);
COMMENT ON COLUMN "drivelicense"."date_of_issue" IS 'Дата выдачи водительского удостоверения';
COMMENT ON COLUMN "drivelicense"."expiration_date" IS 'Дата окончания действия водительского удостоверения';
COMMENT ON COLUMN "drivelicense"."place_of_issue" IS 'Орган выдавший водительское удостоверение';
COMMENT ON COLUMN "drivelicense"."address_of_issue" IS 'Регион, где было выдано водительское удостоверение';
COMMENT ON COLUMN "drivelicense"."number" IS 'Номер водительского удостоверения';
COMMENT ON COLUMN "drivelicense"."categories" IS 'Открытые категории';
COMMENT ON TABLE "drivelicense" IS 'Водительское удостоверение';
CREATE TABLE IF NOT EXISTS "militaryid" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "number" VARCHAR(16) NOT NULL,
    "date_of_birth" TIMESTAMPTZ,
    "place_of_issue" VARCHAR(64),
    "date_of_issue" TIMESTAMPTZ,
    "place_of_birth" VARCHAR(255)
);
COMMENT ON COLUMN "militaryid"."number" IS 'Номер военного билета';
COMMENT ON COLUMN "militaryid"."date_of_birth" IS 'Дата рождения';
COMMENT ON COLUMN "militaryid"."place_of_issue" IS 'Орган выдавший военный билет';
COMMENT ON COLUMN "militaryid"."date_of_issue" IS 'Дата выдачи военного билета';
COMMENT ON COLUMN "militaryid"."place_of_birth" IS 'Место рождения';
COMMENT ON TABLE "militaryid" IS 'Военный билет';
CREATE TABLE IF NOT EXISTS "parkingtimeslot" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "start" TIMESTAMPTZ NOT NULL,
    "end" TIMESTAMPTZ NOT NULL,
    "enable" BOOL NOT NULL  DEFAULT True
);
COMMENT ON TABLE "parkingtimeslot" IS 'Парковочные временные слоты';
CREATE TABLE IF NOT EXISTS "acquireparkinginterval" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "start_interval" TIMESTAMPTZ NOT NULL,
    "end_interval" TIMESTAMPTZ NOT NULL,
    "reserved_interval_id" INT NOT NULL REFERENCES "parkingtimeslot" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "acquireparkinginterval" IS 'Получить временной интервал для парковки авто';
CREATE TABLE IF NOT EXISTS "parkingplace" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "enable" BOOL NOT NULL  DEFAULT True,
    "real_number" SMALLINT NOT NULL,
    "acquire_parking_intervals_id" INT REFERENCES "acquireparkinginterval" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "parkingplace"."real_number" IS 'Номер парковочного места';
COMMENT ON TABLE "parkingplace" IS 'Парковочное место';
CREATE TABLE IF NOT EXISTS "parking" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "max_places" SMALLINT NOT NULL,
    "current_places" SMALLINT,
    "time_slot_interval" INT,
    "parking_places_id" INT REFERENCES "parkingplace" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "parking"."max_places" IS 'Общее количество парковочных мест';
COMMENT ON COLUMN "parking"."current_places" IS 'Текущее количество мест';
COMMENT ON TABLE "parking" IS 'Вся парковка';
CREATE TABLE IF NOT EXISTS "pass" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "rfid" BIGINT,
    "pass_type" VARCHAR(16) NOT NULL,
    "valid_till" TIMESTAMPTZ NOT NULL,
    "valid" BOOL NOT NULL  DEFAULT True
);
COMMENT ON COLUMN "pass"."pass_type" IS 'Тип пропуска (бумажный/карта/лицо)';
COMMENT ON COLUMN "pass"."valid_till" IS 'До какого числа действует пропуск';
COMMENT ON COLUMN "pass"."valid" IS 'Пропуск действителен?';
COMMENT ON TABLE "pass" IS 'Пропуск';
CREATE TABLE IF NOT EXISTS "claim" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "pass_type" VARCHAR(24) NOT NULL,
    "approved" BOOL NOT NULL  DEFAULT False,
    "is_in_blacklist" BOOL NOT NULL  DEFAULT False,
    "pnd_agreement" BOOL NOT NULL  DEFAULT False,
    "information" VARCHAR(255),
    "status" VARCHAR(128) NOT NULL,
    "claim_way_id" INT REFERENCES "claimway" ("id") ON DELETE CASCADE,
    "pass_id_id" INT REFERENCES "pass" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "claim"."pass_type" IS 'Тип пропуска (разовый/временный/постоянный)';
COMMENT ON COLUMN "claim"."approved" IS 'Заявка одобрена?';
COMMENT ON COLUMN "claim"."is_in_blacklist" IS 'В черном списке?';
COMMENT ON COLUMN "claim"."pnd_agreement" IS 'Согласие на обработку ПНД';
COMMENT ON COLUMN "claim"."information" IS 'Любая информация о заявке';
COMMENT ON COLUMN "claim"."status" IS 'Статус заявки(действующая/отработана/просрочена)';
COMMENT ON TABLE "claim" IS 'Заявка на пропуск';
CREATE TABLE IF NOT EXISTS "claimtozone" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "claim_id" INT NOT NULL REFERENCES "claim" ("id") ON DELETE CASCADE,
    "pass_id_id" INT REFERENCES "pass" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "claimtozone" IS 'Заявка на посещение конкретной зоны';
CREATE TABLE IF NOT EXISTS "passport" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "number" BIGINT NOT NULL UNIQUE,
    "division_code" VARCHAR(7),
    "registration" VARCHAR(255),
    "date_of_birth" TIMESTAMPTZ,
    "place_of_birth" VARCHAR(255),
    "gender" VARCHAR(8)
);
COMMENT ON COLUMN "passport"."number" IS 'Номер паспорта';
COMMENT ON COLUMN "passport"."division_code" IS 'Код подразделения';
COMMENT ON COLUMN "passport"."registration" IS 'Прописка';
COMMENT ON COLUMN "passport"."date_of_birth" IS 'Дата рождения';
COMMENT ON COLUMN "passport"."place_of_birth" IS 'Место рождения';
COMMENT ON COLUMN "passport"."gender" IS 'Пол';
COMMENT ON TABLE "passport" IS 'Данные паспорта';
CREATE TABLE IF NOT EXISTS "plugin" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "filename" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "enabled" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "role" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(24) NOT NULL
);
COMMENT ON COLUMN "role"."name" IS 'Название роли';
COMMENT ON TABLE "role" IS 'Роли пользователей для согласований';
CREATE TABLE IF NOT EXISTS "systemuser" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "first_name" VARCHAR(24) NOT NULL,
    "last_name" VARCHAR(24) NOT NULL,
    "middle_name" VARCHAR(24),
    "username" VARCHAR(24) NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "salt" TEXT NOT NULL,
    "last_login" TIMESTAMPTZ,
    "last_logout" TIMESTAMPTZ,
    "expire_session_delta" INT NOT NULL  DEFAULT 86400,
    "phone" VARCHAR(24),
    "email" VARCHAR(36)
);
COMMENT ON COLUMN "systemuser"."first_name" IS 'Имя';
COMMENT ON COLUMN "systemuser"."last_name" IS 'Фамилия';
COMMENT ON COLUMN "systemuser"."middle_name" IS 'Отчество';
COMMENT ON TABLE "systemuser" IS 'Сотрудник компании';
CREATE TABLE IF NOT EXISTS "activedir" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "sid" VARCHAR(128),
    "user_id" INT NOT NULL REFERENCES "systemuser" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "activedir"."sid" IS 'SID пользователя';
COMMENT ON TABLE "activedir" IS 'Данные пользователя из Active Directory';
CREATE TABLE IF NOT EXISTS "systemusersession" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "expire_time" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "logout_time" TIMESTAMPTZ,
    "user_agent" TEXT,
    "salt" TEXT NOT NULL,
    "nonce" TEXT NOT NULL,
    "tag" TEXT NOT NULL,
    "user_id" INT REFERENCES "systemuser" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "systemusersession" IS 'Данные сессии сотрудника компании';
CREATE TABLE IF NOT EXISTS "transport" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "model" VARCHAR(16),
    "number" VARCHAR(16) NOT NULL UNIQUE,
    "color" VARCHAR(16),
    "parking_places_id" INT REFERENCES "parkingplace" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "transport"."number" IS 'Регистрационный номер';
COMMENT ON COLUMN "transport"."color" IS 'Цвет';
COMMENT ON TABLE "transport" IS 'Данные транспорта';
CREATE TABLE IF NOT EXISTS "visitorfoto" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "signature" JSONB,
    "webcam_img" BYTEA,
    "scan_img" BYTEA,
    "car_number_img" BYTEA
);
COMMENT ON COLUMN "visitorfoto"."webcam_img" IS 'Фото с веб-камеры';
COMMENT ON COLUMN "visitorfoto"."scan_img" IS 'Скан документа';
COMMENT ON COLUMN "visitorfoto"."car_number_img" IS 'Фото номера транспорта';
COMMENT ON TABLE "visitorfoto" IS 'Фото посетителя';
CREATE TABLE IF NOT EXISTS "visitor" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deleted" BOOL NOT NULL  DEFAULT False,
    "first_name" VARCHAR(24) NOT NULL,
    "last_name" VARCHAR(24) NOT NULL,
    "middle_name" VARCHAR(24),
    "who_invited" VARCHAR(64),
    "destination" VARCHAR(128),
    "claim_id" INT REFERENCES "claim" ("id") ON DELETE CASCADE,
    "transport_id" INT REFERENCES "transport" ("id") ON DELETE CASCADE,
    "pass_id_id" INT  UNIQUE REFERENCES "pass" ("id") ON DELETE CASCADE,
    "military_id_id" INT  UNIQUE REFERENCES "militaryid" ("id") ON DELETE CASCADE,
    "drive_license_id" INT  UNIQUE REFERENCES "drivelicense" ("id") ON DELETE CASCADE,
    "visitor_foto_id" INT  UNIQUE REFERENCES "visitorfoto" ("id") ON DELETE CASCADE,
    "passport_id" INT  UNIQUE REFERENCES "passport" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "visitor"."first_name" IS 'Имя';
COMMENT ON COLUMN "visitor"."last_name" IS 'Фамилия';
COMMENT ON COLUMN "visitor"."middle_name" IS 'Отчество';
COMMENT ON COLUMN "visitor"."who_invited" IS 'Кто пригласил?';
COMMENT ON COLUMN "visitor"."destination" IS 'Куда идет?';
COMMENT ON TABLE "visitor" IS 'Посетитель';
CREATE TABLE IF NOT EXISTS "blacklist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "level" VARCHAR(24),
    "visitor_id" INT NOT NULL REFERENCES "visitor" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "blacklist"."level" IS 'Уровни нарушений';
COMMENT ON TABLE "blacklist" IS 'Черный список';
CREATE TABLE IF NOT EXISTS "visitsession" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "enter" TIMESTAMPTZ,
    "exit" TIMESTAMPTZ,
    "visitor_id" INT NOT NULL REFERENCES "visitor" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "visitsession"."enter" IS 'Зашел на территорию';
COMMENT ON COLUMN "visitsession"."exit" IS 'Вышел с территории';
COMMENT ON TABLE "visitsession" IS 'Время посещения';
CREATE TABLE IF NOT EXISTS "zone" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(128) NOT NULL
);
COMMENT ON COLUMN "zone"."name" IS 'Название территории';
COMMENT ON TABLE "zone" IS 'Зоны доступа, разрешенные для посещения';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "claimway_role" (
    "claimway_id" INT NOT NULL REFERENCES "claimway" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "claimway_systemuser" (
    "claimway_id" INT NOT NULL REFERENCES "claimway" ("id") ON DELETE CASCADE,
    "systemuser_id" INT NOT NULL REFERENCES "systemuser" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "claimtozone_zone" (
    "claimtozone_id" INT NOT NULL REFERENCES "claimtozone" ("id") ON DELETE CASCADE,
    "zone_id" INT NOT NULL REFERENCES "zone" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "role_systemuser" (
    "systemuser_id" INT NOT NULL REFERENCES "systemuser" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "transport_claim" (
    "transport_id" INT NOT NULL REFERENCES "transport" ("id") ON DELETE CASCADE,
    "claim_id" INT NOT NULL REFERENCES "claim" ("id") ON DELETE CASCADE
);

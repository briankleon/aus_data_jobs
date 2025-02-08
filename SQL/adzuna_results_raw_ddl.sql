CREATE TABLE adzuna_results_raw (
    "Title" TEXT NOT NULL,
    "Company" TEXT NOT NULL,
	"Location" TEXT,
	"Category" TEXT,
	"Contract Type" TEXT,
	"Contract Time" TEXT,
	"Salary Min" TEXT,
	"Salary Max" TEXT,
	"Created" TIMESTAMPTZ NOT NULL,
	"Description" TEXT,
	"Redirect URL" TEXT,
	"timestamp" TIMESTAMP NOT NULL,
    PRIMARY KEY ("Title","Company", "Created", "timestamp")
);
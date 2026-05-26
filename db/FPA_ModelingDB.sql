USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'FPA_ModelingDB')
BEGIN
    ALTER DATABASE FPA_ModelingDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE FPA_ModelingDB;
END
GO

CREATE DATABASE FPA_ModelingDB;
GO

USE FPA_ModelingDB;
GO

CREATE TABLE FinancialScenarios (
    ScenarioID INT IDENTITY(1,1) PRIMARY KEY,
    ScenarioName VARCHAR(100) NOT NULL UNIQUE,
    Author VARCHAR(50) DEFAULT SYSTEM_USER,
    CreatedAt DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE ScenarioParameters (
    ParameterID INT IDENTITY(1,1) PRIMARY KEY,
    ScenarioID INT NOT NULL FOREIGN KEY REFERENCES FinancialScenarios(ScenarioID) ON DELETE CASCADE,
    UnitPrice FLOAT NOT NULL CHECK (UnitPrice > 0),
    Volume INT NOT NULL CHECK (Volume >= 0),
    VolumeVolatility FLOAT NOT NULL CHECK (VolumeVolatility >= 0),
    FixedCosts FLOAT NOT NULL CHECK (FixedCosts >= 0),
    VariableCostPerUnit FLOAT NOT NULL CHECK (VariableCostPerUnit >= 0),
    CostVolatility FLOAT NOT NULL CHECK (CostVolatility >= 0),
    LastUpdatedAt DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE QuantitativeMetrics (
    MetricID INT IDENTITY(1,1) PRIMARY KEY,
    ScenarioID INT NOT NULL FOREIGN KEY REFERENCES FinancialScenarios(ScenarioID) ON DELETE CASCADE,
    SimulationsRun INT NOT NULL,
    GrossProfit_P10 FLOAT NOT NULL,
    GrossProfit_P50 FLOAT NOT NULL,
    GrossProfit_P90 FLOAT NOT NULL,
    Margin_P10 FLOAT NOT NULL,
    Margin_P50 FLOAT NOT NULL,
    Margin_P90 FLOAT NOT NULL,
    RiskOfLossProbability FLOAT NOT NULL,
    CalculatedAt DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE AuditTrail (
    AuditID INT IDENTITY(1,1) PRIMARY KEY,
    ScenarioID INT NOT NULL,
    ActionType VARCHAR(20) NOT NULL, 
    OldVolume INT,
    NewVolume INT,
    OldVolumeVolatility FLOAT,
    NewVolumeVolatility FLOAT,
    ModifiedAt DATETIME DEFAULT GETDATE(),
    ModifiedBy VARCHAR(50) DEFAULT SYSTEM_USER
);
GO

CREATE TRIGGER trg_AuditParameters
ON ScenarioParameters
AFTER UPDATE
AS
BEGIN
    INSERT INTO AuditTrail (ScenarioID, ActionType, OldVolume, NewVolume, OldVolumeVolatility, NewVolumeVolatility)
    SELECT 
        i.ScenarioID,
        'VOLATILITY_UPDATE',
        d.Volume, i.Volume,
        d.VolumeVolatility, i.VolumeVolatility
    FROM inserted i
    INNER JOIN deleted d ON i.ParameterID = d.ParameterID;
END;
GO


-- Select all records from the financial scenarios table
SELECT * FROM FinancialScenarios;

-- Select scenarios created by a specific author
SELECT * FROM FinancialScenarios WHERE Author = 'Finance_Lead';

-- Select scenarios containing the word LATAM in their name
SELECT * FROM FinancialScenarios WHERE ScenarioName LIKE '%LATAM%';

-- Select the most recent scenarios added to the database
SELECT TOP 10 * FROM FinancialScenarios ORDER BY CreatedAt DESC;

-- Select scenarios created in the last 30 days
SELECT * FROM FinancialScenarios WHERE CreatedAt >= DATEADD(day, -30, GETDATE());

-- Count the total number of scenarios per author
SELECT Author, COUNT(*) AS TotalScenarios FROM FinancialScenarios GROUP BY Author;

-- Select distinct authors who have created scenarios
SELECT DISTINCT Author FROM FinancialScenarios;

-- Select scenarios ordered by creation date in ascending order
SELECT * FROM FinancialScenarios ORDER BY CreatedAt ASC;

-- Select the oldest scenario in the database
SELECT TOP 1 * FROM FinancialScenarios ORDER BY CreatedAt ASC;

-- Select scenarios where the name does not contain GLOBAL
SELECT * FROM FinancialScenarios WHERE ScenarioName NOT LIKE '%GLOBAL%';

-- Select all parameters for all scenarios
SELECT * FROM ScenarioParameters;

-- Select parameters where the unit price is greater than 200
SELECT * FROM ScenarioParameters WHERE UnitPrice > 200;

-- Select parameters with a base volume above 10000
SELECT * FROM ScenarioParameters WHERE Volume > 10000;

-- Select parameters ordered by highest fixed costs
SELECT * FROM ScenarioParameters ORDER BY FixedCosts DESC;

-- Calculate the average unit price across all parameters
SELECT AVG(UnitPrice) AS AveragePrice FROM ScenarioParameters;

-- Select parameters with a volume volatility higher than 20 percent
SELECT * FROM ScenarioParameters WHERE VolumeVolatility > 0.20;

-- Select parameters with the lowest cost volatility
SELECT TOP 10 * FROM ScenarioParameters ORDER BY CostVolatility ASC;

-- Calculate the total fixed costs sum for all records
SELECT SUM(FixedCosts) AS TotalFixedCosts FROM ScenarioParameters;

-- Select parameters within a specific range of volume
SELECT * FROM ScenarioParameters WHERE Volume BETWEEN 5000 AND 15000;

-- Select parameters where variable cost is more than half of the unit price
SELECT * FROM ScenarioParameters WHERE VariableCostPerUnit > (UnitPrice * 0.5);

-- Select all quantitative calculation results
SELECT * FROM QuantitativeMetrics;

-- Select metrics where the risk of loss is exactly zero
SELECT * FROM QuantitativeMetrics WHERE RiskOfLossProbability = 0;

-- Select metrics with a risk of loss higher than 15 percent
SELECT * FROM QuantitativeMetrics WHERE RiskOfLossProbability > 15.0;

-- Select the top highest expected gross profits P50
SELECT TOP 10 * FROM QuantitativeMetrics ORDER BY GrossProfit_P50 DESC;

-- Select metrics where the P10 margin is negative
SELECT * FROM QuantitativeMetrics WHERE Margin_P10 < 0;

-- Calculate the average P50 margin across all simulations
SELECT AVG(Margin_P50) AS AverageExpectedMargin FROM QuantitativeMetrics;

-- Select metrics ordered by highest P90 gross profit
SELECT * FROM QuantitativeMetrics ORDER BY GrossProfit_P90 DESC;

-- Count how many scenarios have an acceptable risk under 10 percent
SELECT COUNT(*) AS SafeScenarios FROM QuantitativeMetrics WHERE RiskOfLossProbability < 10.0;

-- Select metrics where the number of simulations run is exactly 10000
SELECT * FROM QuantitativeMetrics WHERE SimulationsRun = 10000;

-- Select the lowest P10 gross profits indicating extreme worst cases
SELECT TOP 10 * FROM QuantitativeMetrics ORDER BY GrossProfit_P10 ASC;

-- Analyze average expected profit and risk distribution grouped by author
SELECT s.Author, 
       COUNT(q.ScenarioID) AS TotalSimulations, 
       AVG(q.GrossProfit_P50) AS AverageExpectedProfit, 
       AVG(q.RiskOfLossProbability) AS AverageRisk
FROM FinancialScenarios s
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
GROUP BY s.Author
ORDER BY AverageExpectedProfit DESC;

-- Identify scenarios where the worst case margin is still positive (Bulletproof scenarios)
SELECT s.ScenarioName, s.Author, q.Margin_P10, q.Margin_P50
FROM FinancialScenarios s
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE q.Margin_P10 > 0
ORDER BY q.Margin_P10 DESC;

-- Correlate high baseline volume with the resulting probability of loss
SELECT p.Volume, AVG(q.RiskOfLossProbability) AS AverageRisk
FROM ScenarioParameters p
INNER JOIN QuantitativeMetrics q ON p.ScenarioID = q.ScenarioID
GROUP BY p.Volume
HAVING COUNT(p.Volume) > 10
ORDER BY p.Volume DESC;

-- Extract strategies that are losing money on average despite running 10000 simulations
SELECT s.ScenarioName, q.GrossProfit_P50, q.RiskOfLossProbability
FROM FinancialScenarios s
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE q.GrossProfit_P50 < 0 AND q.SimulationsRun = 10000;

-- Extract a complete flat analytical view for Machine Learning training 
SELECT s.ScenarioName, 
       p.UnitPrice, 
       p.Volume, 
       p.VolumeVolatility, 
       p.FixedCosts, 
       p.VariableCostPerUnit, 
       q.GrossProfit_P50, 
       q.RiskOfLossProbability
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID;

-- Rank the top performing scenarios within each specific author group using Window Functions
SELECT s.ScenarioName, 
       s.Author, 
       q.GrossProfit_P50,
       RANK() OVER(PARTITION BY s.Author ORDER BY q.GrossProfit_P50 DESC) AS ProfitRankByAuthor
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID;

-- Find outlier scenarios where high volume volatility did not result in high risk
SELECT s.ScenarioName, 
       p.VolumeVolatility, 
       p.FixedCosts, 
       q.RiskOfLossProbability, 
       q.GrossProfit_P50
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE p.VolumeVolatility > 0.30 AND q.RiskOfLossProbability < 5.0
ORDER BY p.VolumeVolatility DESC;

-- Compare scenario parameters against the global average expected profit using Subqueries
SELECT s.ScenarioName, 
       p.UnitPrice, 
       p.VariableCostPerUnit, 
       q.GrossProfit_P50
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE q.GrossProfit_P50 > (SELECT AVG(GrossProfit_P50) FROM QuantitativeMetrics);

-- Identify inefficient pricing where high unit prices yield high risk due to massive fixed costs
SELECT s.ScenarioName, 
       p.UnitPrice, 
       p.FixedCosts, 
       q.RiskOfLossProbability, 
       q.Margin_P50
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE p.UnitPrice > 200 AND q.RiskOfLossProbability > 40.0
ORDER BY q.RiskOfLossProbability DESC;

-- Categorize scenarios into risk buckets using CASE WHEN logic for executive dashboards
SELECT s.ScenarioName,
       p.Volume,
       q.GrossProfit_P50,
       CASE 
           WHEN q.RiskOfLossProbability = 0 THEN 'Risk-Free'
           WHEN q.RiskOfLossProbability <= 15.0 THEN 'Acceptable Risk'
           WHEN q.RiskOfLossProbability <= 50.0 THEN 'High Risk'
           ELSE 'Critical Risk'
       END AS RiskCategory
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID;

-- Calculate moving metrics by measuring the gap between optimistic P90 and pessimistic P10
SELECT s.ScenarioName, 
       p.CostVolatility, 
       (q.GrossProfit_P90 - q.GrossProfit_P10) AS ProfitVariance,
       q.RiskOfLossProbability
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
ORDER BY ProfitVariance DESC;

-- Find optimal business setups high profit, low risk, and logical margins
SELECT s.ScenarioName, 
       s.Author, 
       p.UnitPrice, 
       p.Volume, 
       q.GrossProfit_P50, 
       q.Margin_P50
FROM FinancialScenarios s
INNER JOIN ScenarioParameters p ON s.ScenarioID = p.ScenarioID
INNER JOIN QuantitativeMetrics q ON s.ScenarioID = q.ScenarioID
WHERE q.RiskOfLossProbability < 10.0 
  AND q.GrossProfit_P50 > 500000 
  AND q.Margin_P50 > 25.0
ORDER BY q.GrossProfit_P50 DESC;
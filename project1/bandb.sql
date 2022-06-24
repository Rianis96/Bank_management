DROP DATABASE IF EXISTS BankDb; 
CREATE DATABASE BankDb;

Use BankDb;

Create table tblCustomer (
    CustomerId int not null auto_increment, 
    FirstName varchar(15) not null, 
    LastName varchar(15) not null, 
    Street varchar(30) not null, 
    City varchar(20) not null, 
    State varchar(20) not null, 
    Phone varchar(15) not null, 
    Email varchar(30) not null, 
    CONSTRAINT Pk_Customer PRIMARY KEY (CustomerId)	
);

CREATE TABLE tblAccount  (
    AccountNumber varchar(10) not null, 
    CustomerId int not null, 
    Balance float not null,
    Status varchar(10) not null
);  

ALTER TABLE tblAccount 
ADD CONSTRAINT Pk_Account 
PRIMARY KEY (AccountNumber);

ALTER TABLE tblAccount 
ADD CONSTRAINT Fk_Account_Customer 
FOREIGN KEY (CustomerId) REFERENCES tblCustomer(CustomerId);


CREATE TABLE tblTransaction (
    TransactionId int not null auto_increment,
    AccountNumber varchar(10) not null,  
    TransactionDate varchar(15) not null, 
    TransactionAmount float not null, 
    TransactionType varchar(10) not null, 
	CONSTRAINT Pk_Transaction PRIMARY KEY (TransactionId)
);

ALTER TABLE tblTransaction 
ADD CONSTRAINT Fk_Account_Transaction 
FOREIGN KEY (AccountNumber)
REFERENCES tblAccount (AccountNumber);


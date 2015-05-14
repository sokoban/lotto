create table Lottonumber(
Lnumber integer not null,
firstnum integer not null,
secondnum integer not null,
thirdnum integer not null,
fourthnum integer not null,
fifthnum integer not null,
sixthnum integer not null,
luckynum integer not null,
regdt datetime null)

create table genlottonumber(
seqno integer not null AUTO_INCREMENT,
username varchar(100) null,
genmethod varchar(30) not null,
firstnum integer not null,
secondnum integer not null,
thirdnum integer not null,
fourthnum integer not null,
fifthnum integer not null,
sixthnum integer not null,
luckynum integer not null,
regdt datetime null,
Primary key (seqno)
)


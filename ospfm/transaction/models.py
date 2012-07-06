#    Copyright 2012 Sebastien Maccagnoni-Munch
#
#    This file is part of OSPFM.
#
#    OSPFM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OSPFM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with OSPFM.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy import Boolean, Column, Date, ForeignKey,\
                       Integer, Numeric, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint

from ospfm.database import Base


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    currency_id = Column(ForeignKey('currency.id'))
    start_balance = Column(Numeric(15, 3), nullable=False)

    currency = relationship('Currency')
    account_owners = relationship('AccountOwner', cascade='all, delete-orphan')
    transactions_account = relationship('TransactionAccount',
                                        cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'currency': self.currency.symbol,
            'start_balance': self.start_balance
        }


class AccountOwner(Base):
    __tablename__ = 'accountowner'
    account_id = Column(ForeignKey('account.id'), primary_key=True)
    owner_username = Column(ForeignKey('user.username'), primary_key=True)

    account = relationship('Account')
    owner = relationship('User')


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    owner_username = Column(ForeignKey('user.username'), nullable=False)
    parent_id = Column(ForeignKey('category.id'))
    name = Column(String(50), nullable=False)

    owner = relationship('User')
    children = relationship('Category',
                            backref=backref('parent', remote_side=[id]),
                            order_by='Category.name')

    # XXX When defining relationships, don't forget "DELETE CASCADE"

    def as_dict(self, parent=True):
        desc = {
            'id': self.id,
            'name': self.name,
        }
        if parent and self.parent_id:
            desc['parent'] = self.parent_id
        if self.children:
            desc['children'] = [c.as_dict(False) for c in self.children]
        return desc

    def contains_category(self, categoryid):
        if self.id == categoryid:
            return True
        if self.children:
            for c in self.children:
                if c.contains_category(categoryid):
                    return True
        return False


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    owner_username = Column(ForeignKey('user.username'), nullable=False)
    description = Column(String(200), nullable=False)
    original_description = Column(String(200))
    amount = Column(Numeric(15, 3), nullable=False)
    currency_id = Column(ForeignKey('currency.id'), nullable=False)
    date = Column(Date, nullable=False)

    owner = relationship('User')
    currency = relationship('Currency')

class TransactionAccount(Base):
    __tablename__ = 'transactionaccount'
    transaction_id = Column(ForeignKey('transaction.id'), primary_key=True)
    account_id = Column(ForeignKey('account.id'), primary_key=True)
    amount = Column(Numeric(15, 3), nullable=False)
    verified = Column(Boolean, nullable=False)

    transaction = relationship('Transaction')
    account = relationship('Account')

class TransactionCategory(Base):
    __tablename__ = 'transactioncategory'
    transaction_id = Column(ForeignKey('transaction.id'), primary_key=True)
    category_id = Column(ForeignKey('category.id'), primary_key=True)
    amount = Column(Numeric(15, 3), nullable=False)

    transaction = relationship('Transaction')
    category = relationship('Category')

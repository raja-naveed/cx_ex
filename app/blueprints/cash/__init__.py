from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from app import db
from app.models import CashLedger, CashTransactionType
from decimal import Decimal

bp = Blueprint('cash', __name__)

class CashTransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01, max=100000)])
    submit = SubmitField('Submit')

@bp.route('/')
@login_required
def index():
    balance = current_user.get_cash_balance()
    transactions = CashLedger.query.filter_by(user_id=current_user.id).order_by(CashLedger.created_at.desc()).limit(20).all()
    return render_template('cash/index.html', balance=balance, transactions=transactions)

@bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = CashTransactionForm()
    if form.validate_on_submit():
        transaction = CashLedger(
            user_id=current_user.id,
            transaction_type=CashTransactionType.DEPOSIT,
            amount=form.amount.data,
            description='Cash deposit'
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Deposited ${form.amount.data}', 'success')
        return redirect(url_for('cash.index'))
    
    return render_template('cash/deposit.html', form=form)

@bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    form = CashTransactionForm()
    if form.validate_on_submit():
        current_balance = current_user.get_cash_balance()
        if form.amount.data > current_balance:
            flash('Insufficient funds', 'error')
            return render_template('cash/withdraw.html', form=form)
        
        transaction = CashLedger(
            user_id=current_user.id,
            transaction_type=CashTransactionType.WITHDRAWAL,
            amount=-form.amount.data,
            description='Cash withdrawal'
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Withdrew ${form.amount.data}', 'success')
        return redirect(url_for('cash.index'))
    
    return render_template('cash/withdraw.html', form=form)
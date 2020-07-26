# Copyright 2017 Twin Tech Labs. All rights reserved

from flask import Blueprint, redirect, render_template, current_app, abort
from flask import request, url_for, flash, send_from_directory, jsonify, render_template_string
from flask_user import current_user, login_required, roles_accepted

from app import db
from app.models.user_models import UserProfileForm, User, UsersRoles, Role
from app.models.drive_models import DriveForm, Drive, DriveLog
from app.utils.forms import ConfirmationForm
from psutil._common import bytes2human
import collections
from datetime import datetime
import uuid, json, os
import psutil


# When using a Flask app factory we must use a blueprint to avoid needing 'app' for '@app.route'
main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The User page is accessible to authenticated users (users that have logged in)
#@main_blueprint.route('/')
#def member_page():
#    if not current_user.is_authenticated:
#        return redirect(url_for('user.login'))
#    return render_template('pages/member_base.html')
@main_blueprint.route('/')
def status_page():
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))

    mount_status = Drive.query.filter_by(mounted=True).one_or_none()
    mounted_drive = "None"
    general_data = get_general_data()
    log_entries = db.session.query(DriveLog,Drive.name).join(Drive).limit(100).all()
    if mount_status:
        mounted_drive = mount_status.name
    return render_template('status.html', mount_status=mount_status, mounted_drive=mounted_drive,
     general_data=general_data, log_entries=log_entries)

def get_general_data():
    # General statistics for homepage
    general_data = collections.namedtuple('Sensor',['cpu_temp','load','cpu_percent','uptime'])
    
    general_data.cpu_temp = round(psutil.sensors_temperatures().get("cpu_thermal")[0].current, 1)
    # 5 minute load average
    general_data.load = psutil.getloadavg()[1]
    general_data.cpu_percent = psutil.cpu_percent()

    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    if uptime.days > 0:
        if uptime.days > 1:
            day_string = "Days"
        else: 
            day_string = "Day"
        uptime_day = f'{uptime.days} {day_string} '
    else:
        uptime_day = ""
    # Hours
    if uptime.seconds//3600 != 0:
        if uptime.seconds//3600 > 1:
            hour_string = "Hours"
        else: 
            hour_string = "Hour"
        uptime_hour = f'{uptime.seconds//3600} {hour_string} '
    else:
        uptime_hour = ""

    # Minutes
    if (uptime.seconds//60)%60 != 0:
        if (uptime.seconds//60)%60 > 1:
            minute_string = "Minutes"
        else: 
            minute_string = "Minute"
        uptime_min = f'{(uptime.seconds//60)%60} {minute_string}'
    else:
        uptime_min = ""

    general_data.uptime = f"{uptime_day}{uptime_hour}{uptime_min}"

    return general_data



# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_accepted('admin')
def admin_page():
    return redirect(url_for('main.user_admin_page'))

@main_blueprint.route('/users')
@roles_accepted('admin')
def user_admin_page():
    users = User.query.all()
    return render_template('pages/admin/users.html', users=users)

@main_blueprint.route('/create_user', methods=['GET', 'POST'])
@roles_accepted('admin')
def create_user_page():
    if current_app.config.get('USER_LDAP', False):
        abort(400)

    form = UserProfileForm()
    roles = Role.query.all()
    form.roles.choices = [(x.id,x.name) for x in roles]

    if form.validate():
        user = User.query.filter(User.email == request.form['email']).first()
        if not user:
            user = User(email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        password=current_app.user_manager.hash_password(form.password.data),
                        active=True,
                        email_confirmed_at=datetime.datetime.utcnow())
            db.session.add(user)
            db.session.commit()
            allowed_roles = form.roles.data
            for role in roles:
                if role.id not in allowed_roles:
                    if role in user.roles:
                        user.roles.remove(role)
                else:
                    if role not in user.roles:
                        user.roles.append(role)
            db.session.commit()
            flash('You successfully created the new user.', 'success')
            return redirect(url_for('main.user_admin_page'))
        flash('A user with that email address already exists', 'error')
    return render_template('pages/admin/create_user.html', form=form)


@main_blueprint.route('/users/<user_id>/delete', methods=['GET', 'POST'])
@roles_accepted('admin')
def delete_user_page(user_id):
    if current_app.config.get('USER_LDAP', False):
        abort(400)
    form = ConfirmationForm()
    user = User.query.filter(User.id == user_id).first()
    if not user:
        abort(404)
    if form.validate():
        db.session.query(UsersRoles).filter_by(user_id = user_id).delete()
        db.session.query(User).filter_by(id = user_id).delete()
        db.session.commit()
        flash('You successfully deleted your user!', 'success')
        return redirect(url_for('main.user_admin_page'))
    return render_template('pages/admin/delete_user.html', form=form)


@main_blueprint.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@roles_accepted('admin')
def edit_user_page(user_id):
    if current_app.config.get('USER_LDAP', False):
        abort(400)

    user = User.query.filter(User.id == user_id).first()
    if not user:
        abort(404)

    form = UserProfileForm(obj=user)
    roles = Role.query.all()
    form.roles.choices = [(x.id,x.name) for x in roles]

    if form.validate():
        if 'password' in request.form and len(request.form['password']) >= 8:
            user.password = current_app.user_manager.hash_password(request.form['password'])
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.active = form.active.data

        allowed_roles = form.roles.data
        for role in roles:
            if role.id not in allowed_roles:
                if role in user.roles:
                    user.roles.remove(role)
            else:
                if role not in user.roles:
                    user.roles.append(role)

        db.session.commit()
        flash('You successfully edited the user.', 'success')
        return redirect(url_for('main.user_admin_page'))

    form.roles.data = [role.id for role in user.roles]
    return render_template('pages/admin/edit_user.html', form=form)

@main_blueprint.route('/pages/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    if current_app.config.get('USER_LDAP', False):
        abort(400)

    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.user_profile_page'))

    # Process GET or invalid POST
    return render_template('pages/user_profile_page.html',
                           current_user=current_user,
                           form=form)

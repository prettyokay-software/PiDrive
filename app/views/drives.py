from flask import Blueprint, redirect, render_template, current_app
from flask import request, url_for, flash, send_from_directory, jsonify, render_template_string
from flask_user import current_user, login_required, roles_accepted

from flask import Flask, session, redirect, url_for, request, render_template, jsonify, abort
from app import db
from app.models import user_models as users
from app.models import drive_models as drives
from app.utils import forms
from datetime import datetime

import time
import uuid


# When using a Flask app factory we must use a blueprint to avoid needing 'app' for '@apikeys_blueprint.route'
drives_blueprint = Blueprint('drives', __name__, template_folder='templates')

@drives_blueprint.route('/drives')
@roles_accepted('dev', 'admin')
def drives_index():
    #all_drives = db.Query(drives).all()
    all_drives = drives.Drive.query.all()
    return render_template("drives/list.html", all_drives=all_drives)


@drives_blueprint.route('/drives/create_drive', methods=['GET', 'POST'])
@roles_accepted('dev', 'admin')
def drives_create():
    form = drives.DriveForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form.get('name', None)
        description = request.form.get('description', None)
        path = request.form.get('path', None)
        size = request.form.get('size', None)
        new_drive = drives.Drive(name=name, description=description, path=path, size=size, mounted=False, date_created=datetime.now())
        db.session.add(new_drive)
        db.session.flush()
        drive_log = drives.DriveLog(drive_id=new_drive.id, action="Create", data="Initial Drive Creation", user=current_user.username, action_date=new_drive.date_created)
        db.session.add(drive_log)
        db.session.commit()
        return render_template("drives/newdrive.html", name=name, description=description, path=path, size=size, mounted=False, date_created=datetime.now())
    return render_template("drives/create.html", form=form)


@drives_blueprint.route('/drives/delete/<drive_id>', methods=['GET', 'POST'])
@roles_accepted('dev', 'admin')
def drives_delete(drive_id):
    form = forms.ConfirmationForm(request.form)
    name = drives.Drive.query.filter_by(id=drive_id).first()

    if request.method == 'POST':
        remove_drive = drives.Drive.query.filter_by(id=drive_id).first()
        if remove_drive:
            db.session.delete(remove_drive)
            db.session.commit()
        return redirect(url_for('drives.drives_index'))

    return render_template("drives/delete.html", form=form, drive_id=drive_id, name=name.name)

@drives_blueprint.route('/drives/mount', methods=['Get'])
@drives_blueprint.route('/drives/mount/<drive_id>', methods=['PUT'])
@roles_accepted('dev', 'admin')
def drives_mount(drive_id=None): 
    if request.method == 'PUT' and drive_id != None:
        current_mount = drives.Drive.query.filter_by(mounted=True).one_or_none()
        #new_mount = drives.Drive.query.filter_by(id=request.values.get('drive_id')).first()
        new_mount = drives.Drive.query.filter_by(id=drive_id).first()

        if current_mount:
            current_mount.mounted = False
            db.session.add(current_mount)
            unmount_log = drives.DriveLog(drive_id = current_mount.id,action = "Unmount", data = "Drive is being unmounted",
                action_date=datetime.now(), user = current_user.username)
            db.session.add(unmount_log)
            db.session.flush()
            if current_mount.id == new_mount.id:
                db.session.commit()
                return "Unmounted {} successfully".format(current_mount.name)

        new_mount.mounted = True
        mount_log = drives.DriveLog(drive_id = new_mount.id,action = "Mount", data = "Drive is being mounted",
            action_date=datetime.now(), user = current_user.username)

        db.session.add(mount_log)
        db.session.add(new_mount)
        db.session.commit()
        return "Mounted {} successfully".format(new_mount.name)
    return redirect(url_for('drives.drives_index'))
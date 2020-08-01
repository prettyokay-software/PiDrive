from flask import Blueprint, redirect, render_template, current_app
from flask import request, url_for, flash, send_from_directory, jsonify, render_template_string
from flask_user import current_user, login_required, roles_accepted
from flask import Flask, session, redirect, url_for, request, render_template, jsonify, abort

from app import db
from app.models import user_models as users
from app.models import drive_models as drives
from app.utils import forms, drive_utility
from datetime import datetime
from pathlib import Path

import os
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

        # Data sanitizing time!
        full_path = drive_utility.SanitizeDrivePath(path, name)

        # Create the image
        creation_result = drive_utility.CreateDriveImage(full_path, size)

        if creation_result.success:
            new_drive = drives.Drive(name=name, description=description, path=full_path, size=size, free_space=size, mounted=False, date_created=datetime.now())
            db.session.add(new_drive)
            db.session.flush()
            drive_log = drives.DriveLog(drive_id=new_drive.id, action="Create", data="Created image {} - {}GB".format(full_path, size), user=current_user.username, action_date=new_drive.date_created)
            db.session.add(drive_log)
            db.session.commit()
            return render_template("drives/newdrive.html", name=name, description=description, path=full_path, size=size, mounted=False, date_created=datetime.now())
        else:
            flash("Drive Creation Failed {}".format(creation_result.message),"error")
            os.remove(full_path)
            return render_template("drives/create.html", form=form)

    return render_template("drives/create.html", form=form)


@drives_blueprint.route('/drives/delete/<drive_id>', methods=['GET', 'POST'])
@roles_accepted('dev', 'admin')
def drives_delete(drive_id):
    form = forms.ConfirmationForm(request.form)
    name = drives.Drive.query.filter_by(id=drive_id).first()

    if request.method == 'POST':
        remove_drive = drives.Drive.query.filter_by(id=drive_id).first()

        if Path(remove_drive.path).exists():
            # If for some reason the file doesn't exist, just move on            
            os.remove(remove_drive.path)

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
            drive_utility.RemoveUSBDrive((current_mount.path))
            unmount_log = drives.DriveLog(drive_id = current_mount.id,action = "Unmount", data = "Drive has been unmounted",
                action_date=datetime.now(), user = current_user.username)
            db.session.add(unmount_log)
            db.session.flush()
            # If new and old mount id match, we're just unmounting the currently mounted drive
            if current_mount.id == new_mount.id:
                db.session.commit()
                return "Unmounted {} successfully".format(current_mount.name)

        drive_utility.InsertUSBDrive(new_mount.path)
        new_mount.mounted = True
        mount_log = drives.DriveLog(drive_id = new_mount.id,action = "Mount", data = "Drive has been mounted",
            action_date=datetime.now(), user = current_user.username)

        db.session.add(mount_log)
        db.session.add(new_mount)
        db.session.commit()

        flash("{} is now connected".format(new_mount.name),"success")

        return "Mounted {} successfully".format(new_mount.name)
    return redirect(url_for('drives.drives_index'))
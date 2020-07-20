from app import db
from app.models import user_models as users
from app.models import drive_models as drives
from app.utils import forms
from datetime import datetime
from pathlib import Path
from pathvalidate import sanitize_filepath


import uuid
import ctypes
import imagemounter
import subprocess
import parted
import collections
import os
import kmodpy


def CreateDriveImage (full_path, drive_size):
    # https://www.wefearchange.org/2017/01/sparsefiles.rst.html
    # Create a namedtuple to return data to the caller
    return_data = collections.namedtuple('Result',['success','message'])

    # We're storing the drive sizes in GB, but truncate wants it in bytes
    drive_size_bytes = float(drive_size) * 1073741824
    
    # Create the actual file
    # File exists check happens during touch
    try:
        drive_image = Path(full_path)
        drive_image.touch()
        os.truncate(str(drive_image), drive_size_bytes)
    except FileExistsError:
        return return_data(False,"File Already Exists at {}".format(full_path))
    except Exception as e:
        return return_data(False, e)
    
    # Is it really there?
    if Path(full_path).exists():
        format_result = FormatDriveImage(full_path)
        if format_result.success:
            return return_data(True, "Successfully Created and Formatted {}".format(full_path))
        else:
            # DELETE IMAGE ON FAILURE
            return return_data(False,"Failed to Format {} ERROR: {}".format(full_path, format_result.message))
    else: 
        return return_data(False, "Creation Failed for an Unknown Reason")

def SanitizeDrivePath (path, drive_name):
    # Check for trailing / on path and add if needed
    if path[-1] != "/":
        path = path+"/"

    # Add .img to drive name
    if drive_name[-4:] != ".img":
        drive_name = drive_name+".img"

    full_path = sanitize_filepath(path + drive_name, platform="auto")

    return full_path

def FormatDriveImage (full_path):
    # Formats a drive image as FAT32 using the full available space
        return_data = collections.namedtuple('Result',['success','message'])

        # Make sure the file we're working with already exists
        if not Path(full_path).exists():
            return return_data(False, "Path not found {}".format(full_path))

        try:
            # Build the device and disk objects
            disk_device = parted.getDevice(full_path)
            new_disk = parted.freshDisk(disk_device,"gpt")

            geometry = parted.Geometry(device=disk_device, start=1,
                                   length=disk_device.getLength() - 1)
            os.path.basename(full_path)
            filesystem = parted.FileSystem(type='fat32', geometry=geometry)
            new_partition = parted.Partition(
                disk=new_disk,
                type=parted.PARTITION_NORMAL,
                fs = filesystem,
                geometry=geometry
            )

            new_disk.addPartition(partition=new_partition, constraint=disk_device.optimalAlignedConstraint)
            new_disk.commit()

        except Exception as e:
            return return_data(False,e)

        return return_data(True, "")

def MountDrive(full_path):
    # Mount a drive image to allow browsing
    return_data = collections.namedtuple('Result',['success','message'])

    mount_location = os.path.dirname(os.path.abspath(__file__))+"/image_mount"

    parser = imagemounter.ImageParser(full_path,read_write=True,mountdir=mount_location,pretty=True)
    parser.init(single=True)
    mount_result = parser.mount_disks()

    if mount_result:
        return return_data(True,"Disk mounted successfully")
    else:
        return return_data(False, "Mount Failed")

def InsertUSBDrive(full_path):
    # Reconfigures g_mass_storage to present the selected disk image

    #idVendor=0x0781 idProduct=0x5572 bcdDevice=0x011a iManufacturer="PiDrive" iProduct="Virtual_USB_Drive" iSerialNumber="0DEADBEEF0"

    # I wish I was smart enough to make this work, it seems so much cleaner....
    #km = kmodpy.Kmod()
    #https://stackoverflow.com/questions/23852311/different-behaviour-of-ctypes-c-char-p
    #options = "file='{}' stall=0 removable=0 ro=0".format(full_path)
    #km.modprobe("g_mass_storage", 
    # extra_options=ctypes.c_char_p(options.encode('utf-8')))

    result = subprocess.run(['modprobe', 'g_mass_storage', 'file={}'.format(full_path), 'stall=0', 'removable=0', 'ro=0'], stdout=subprocess.PIPE)

def RemoveUSBDrive(full_path):
    #km = kmodpy.Kmod()
    #km.rmmod("g_mass_storage")
    result = subprocess.run(['modprobe', '-r', 'g_mass_storage'])

#def GetDriveFreeSpace(full_path): 
# Uninstall

This guide tells you different ways to uninstall OCLP and/or patches.

## Delete everything and revert back to native macOS

Boot a native macOS installer, go to Disk Utility and choose View -> Show All Devices. Wipe the full disk by choosing the top option on the left sidebar and start macOS installation.

[Reset NVRAM](https://support.apple.com/HT204063) afterwards.

## Uninstalling the application

### Version 1.5.0 and newer

Version 1.5.0 and newer use a Privileged Helper Tool that requires more thorough uninstallation than previous versions. Download the uninstaller package from [the releases page.](https://github.com/dortania/OpenCore-Legacy-Patcher/releases)

### Version 1.4.3 and older.

Navigate to `/Library/Application Support/` and delete the Dortania folder.

## Reverting root patches

Open the OCLP application and go into the Post Install Root Patch menu, choose Revert Root Patches.

If you're planning to revert back to native version, you don't have to do this. Root patches get wiped when you wipe the disk.

## Uninstalling the bootloader

1. Remove OpenCore either from the USB or internal drive

  * You'll need to mount the drive's EFI partition, and delete the `EFI/OC` and `System` folders
    * Note: **Do not** delete the entire EFI folder, this will likely break any existing Windows and Linux installations.
    * [See here for an example on how to mount](https://dortania.github.io/OpenCore-Post-Install/universal/oc2hdd.html)
    * For 5K iMac users, you will also need to delete `boot.efi` on the root of the EFI partition.

2. [Reset NVRAM](https://support.apple.com/HT204063)

:::warning

Note that after you remove OpenCore, your Mac will no longer boot and show the "prohibited" symbol. Be prepared to have a bootable USB drive with either OpenCore or natively-supported version of macOS before you uninstall the bootloader.

* This does not apply to native Macs just using OpenCore to achieve features like AirPlay to Mac and Sidecar, but it is still recommended to reinstall macOS after removing OpenCore, if using SMBIOS spoofing to enable Universal Control and other features.
:::



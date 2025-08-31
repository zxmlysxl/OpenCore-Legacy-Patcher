# macOS Sequoia

![](./images/macos-sequoia.png)

Another year, another release.

This time Apple dropped surprisingly few amount of Macs. With the release of OpenCore Legacy Patcher 2.0.0, early support for macOS Sequoia has been implemented.


## Newly dropped hardware

* MacBookAir8,1 :       MacBook Air (2018)
* MacBookAir8,2 :       MacBook Air (2019)

## Current status

OpenCore Legacy Patcher 2.0.0 will support Sequoia for most models normally supported by the Patcher, however some challenges remain. You can find information about them below.

Unfortunately due to T2 related problems, the recently dropped MacBookAir8,x models cannot be supported at this time. We have made some progress on this issue, but panics are still occurring and there is still a significant amount of development work to do before T2 machines may even get to the install screen. We cannot provide any estimate on when T2 machines will be supported.

[More information here](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1136)

## Non-functional features

On majority of patched Macs, iPhone Mirroring and Apple Intelligence won't be functional.

iPhone Mirroring requires T2 for attestation and Apple Intelligence requires an NPU only found in Apple Silicon, the patcher is unable to provide a fix for these as they're hardware requirements.

## Issues

* [Dual socket CPUs with Mac Pros and Xserve](#dual-socket-cpus-with-mac-pro-2008-and-xserve-2008)
* [T2 Security chip](#t2-security-chip)
* [USB 1.1 (OHCI/UHCI) Support](#usb-1-1-ohci-uhci-support)
* [Graphics support and issues](#graphics-support-and-issues)


### Dual socket CPUs with Mac Pro 2008 and Xserve 2008

Booting Sequoia on Mac Pro 2008 (MacPro3,1) or Xserve 2008 (Xserve2,1) with more than 4 cores will cause Sequoia to panic. OpenCore Legacy Patcher will automatically disable additional cores.

This is due to the dual socket nature of the machine, and likely some firmware/ACPI table incompatibility. 

**If building OpenCore for older OS, this limitation can be disabled in Settings -> Build -> "MacPro3,1/Xserve2,1 Workaround".** 

::: warning Note

Dual booting Sequoia and older will not be possible with all cores enabled due to reasons described before. In these cases you will be limited to 4 cores.

:::

### T2 security chip

The current biggest issue we face with supporting the MacBookAir8,x (2018/19) series is the T2 chip's lack of communication when booted through OpenCorePkg.

What happens when one of these units boots through OpenCorePkg is that AppleKeyStore.kext panics due to timeouts with the T2 chip:

```
"AppleKeyStore":3212:0: sks timeout strike 18
"AppleKeyStore":3212:0: sks timeout strike 19
"AppleKeyStore":3212:0: sks timeout strike 20
panic(cpu 0 caller 0xffffff801cd12509): "AppleSEPManager panic for "AppleKeyStore": sks request timeout" @AppleSEPManagerIntel.cpp:809
```

This affects not only macOS Sequoia, but macOS Ventura and Sonoma are confirmed to have the same issue. Thus an underlying problem with the MacBookAir8,x's firmware where it is not happy with OpenCorePkg.

* MacBookPro15,2, MacBookPro16,2 and Macmini8,1 do not exhibit these issues in local testing
* MacPro7,1 does seem to surprisingly based on reports: [MacPro7,1 - OpenCorePkg](https://forums.macrumors.com/threads/manually-configured-opencore-on-the-mac-pro.2207814/post-29418464)
  * Notes from this report were unsuccessful locally: [Cannot boot MacPro7,1 #1487](https://github.com/acidanthera/bugtracker/issues/1487)

We have made some progress on this issue, but panics are still occurring and there is still a significant amount of development work to do before T2 machines may even get to the install screen. We cannot provide any estimate on when T2 machines will be supported.

### USB 1.1 (OHCI/UHCI) Support

For Penryn systems, pre-2013 Mac Pros and Xserve, USB 1.1 support was outright removed in macOS Ventura, therefore this applies all the way to Sequoia.
While USB 1.1 may seem unimportant, it handles many important devices on your system. These include:

* Keyboard and Trackpad for laptops
* IR Receivers
* Bluetooth

Refer to [the troubleshooting page](https://dortania.github.io/OpenCore-Legacy-Patcher/TROUBLESHOOT-HARDWARE.html#keyboard-mouse-and-trackpad-not-working-in-installer-or-after-update) on how to workaround this issue.


### Graphics support and issues
This build includes both Legacy Metal and non-Metal patches for macOS Sequoia. Refer to the following links for more information about Legacy Metal and non-Metal support and their respective issues.

* [Legacy Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/1008)
* [Non-Metal](https://github.com/dortania/OpenCore-Legacy-Patcher/issues/108)

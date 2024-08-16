"""
sys_patch_dict.py: Dictionary defining patch sets used during Root Volume patching (sys_patch.py)
"""

import packaging.version

from . import os_data


class SystemPatchDictionary():
    """
    Library for generating patch sets for sys_patch.py and supporting modules

    Usage:
        >>> patchsets = SystemPatchDictionary(22, 0, [20, 21, 22], "13.0").patchset_dict


    Patchset Schema:
        Supports following types of higher level keys:
        - OS Support: Supported OSes by patches
            - Minimum OS Support:  Minimum supported OS version
                - OS Major:          Major XNU Kernel version
                - OS Minor:          Minor XNU Kernel version
            - Maximum OS Support:  Maximum supported OS version
                - OS Major:          Major XNU Kernel version
                - OS Minor:          Minor XNU Kernel version
        - Install: Files to install to root volume
            - Location:
                - File (dict: { "File": "Source" })
        - Install Non-Root: Files to install to data partition
            - Location:
                - File (dict: { "File": "Source" })
        - Remove: Files to remove
            - Location:
                - File (array: [ "File" ])
        - Remove Non-Root: Files to remove from data partition
            - Location:
                - File (array: [ "File" ])
        - Processes: Additional processes to run
            - Process (dict: { "Process": "Requires Root" })
        - Display Name: User-friendly name (string, "" if user-friendly name is not required)


    Schema file storage is based off the origin, ie. '10.13.6/System/Library/Extensions/IOSurface.kext':

        "Install": {
            "/System/Library/Extensions": {
                "IOSurface.kext": "10.13.6",
            },
        },

    Note: Stubbed binaries are OS specific, thus use the 'self.os_major' variable to denounce which folder variant to use
    """

    def __init__(self, os_major: int, os_minor: int, non_metal_os_support: list, marketing_version: str) -> None:
        """
        Parameters:
            os_major              (int): Major XNU Kernel version
            os_minor              (int): Minor XNU Kernel version
            non_metal_os_support (list): List of supported non-metal OSes (XNU Major Versions)
            marketing_version     (str): Marketing version of the OS

        'non_metal_os_support' is assumed to be sorted from oldest to newest
        """

        self.os_major:              int = os_major
        self.os_minor:              int = os_minor
        self.os_float:            float = float(f"{self.os_major}.{self.os_minor}")
        self.non_metal_os_support: list = non_metal_os_support
        self.patchset_dict:        dict = {}
        self.marketing_version:     str = marketing_version

        self.affected_by_cve_2024_23227: bool = self.__is_affect_by_cve_2024_23227()

        # XNU Kernel versions
        self.macOS_12_0_B7:       float = 21.1
        self.macOS_12_4:          float = 21.5
        self.macOS_12_5:          float = 21.6
        self.macOS_13_3:          float = 22.4
        self.macOS_14_1:          float = 23.1
        self.macOS_14_2:          float = 23.2
        self.macOS_14_4:          float = 23.4

        self._generate_sys_patch_dict()


    def __resolve_ivy_bridge_framebuffers(self) -> str:
        """
        Resolve patchset directory for Ivy Bridge framebuffers:
        - AppleIntelFramebufferCapri.kext
        - AppleIntelHD4000Graphics.kext
        """
        if self.os_major < os_data.os_data.sonoma:
            return "11.7.10"
        if self.os_float < self.macOS_14_4:
            return "11.7.10-23"
        return "11.7.10-23.4"


    def __resolve_kepler_geforce_framebuffers(self) -> str:
        """
        Resolve patchset directory for GeForce.kext
        """
        if self.os_major < os_data.os_data.sonoma:
            return "12.0 Beta 6"
        if self.os_float < self.macOS_14_4:
            return "12.0 Beta 6-23"
        return "12.0 Beta 6-23.4"


    def __resolve_monterey_framebuffers(self) -> str:
        """
        Resolve patchset directory for framebuffers last supported in Monterey:
        - AppleIntelBDWGraphics.kext
        - AppleIntelBDWGraphicsFramebuffer.kext
        - AppleIntelFramebufferAzul.kext
        - AppleIntelHD5000Graphics.kext
        - AppleIntelSKLGraphics.kext
        - AppleIntelSKLGraphicsFramebuffer.kext
        - AMDRadeonX4000.kext
        - AMDRadeonX5000.kext
        """
        if self.os_major < os_data.os_data.sonoma:
            return "12.5"
        if self.os_float < self.macOS_14_4:
            return "12.5-23"
        return "12.5-23.4"


    def __is_affect_by_cve_2024_23227(self) -> bool:
        """
        CVE-2024-23227 broke our airportd patches for 12.7.4, 13.6.5 and 14.4

        Note that since the XNU version's security patch level is not increment
        """

        if self.os_major > os_data.os_data.sonoma:
            return True

        parsed_version = packaging.version.parse(self.marketing_version)
        if self.marketing_version.startswith("12"):
            return parsed_version >= packaging.version.parse("12.7.4")
        if self.marketing_version.startswith("13"):
            return parsed_version >= packaging.version.parse("13.6.5")
        if self.marketing_version.startswith("14"):
            return parsed_version >= packaging.version.parse("14.4")

        return False


    def _generate_sys_patch_dict(self):
        """
        Generates the sys_patch_dict dictionary
        """

        self.patchset_dict = {
            "Graphics": {
                "Non-Metal Common": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": self.non_metal_os_support[-1],
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "IOSurface.kext": "10.15.7",
                        },
                        "/System/Library/Frameworks": {
                            "OpenGL.framework":       "10.14.3",
                            "CoreDisplay.framework": f"10.14.4-{self.os_major}",
                            "IOSurface.framework":   f"10.15.7-{self.os_major}",
                            "QuartzCore.framework":  f"10.15.7-{self.os_major}",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "GPUSupport.framework": "10.14.3",
                            "SkyLight.framework":  f"10.14.6-{self.os_major}",
                            **({"FaceCore.framework":  f"13.5"} if self.os_major >= os_data.os_data.sonoma else {}),
                        },
                        "/System/Applications": {
                            **({ "Photo Booth.app": "11.7.9"} if self.os_major >= os_data.os_data.monterey else {}),
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            "AMDRadeonX4000.kext",
                            "AMDRadeonX4000HWServices.kext",
                            "AMDRadeonX5000.kext",
                            "AMDRadeonX5000HWServices.kext",
                            "AMDRadeonX6000.kext",
                            "AMDRadeonX6000Framebuffer.kext",
                            "AMDRadeonX6000HWServices.kext",
                            "AppleIntelBDWGraphics.kext",
                            "AppleIntelBDWGraphicsFramebuffer.kext",
                            "AppleIntelCFLGraphicsFramebuffer.kext",
                            "AppleIntelHD4000Graphics.kext",
                            "AppleIntelHD5000Graphics.kext",
                            "AppleIntelICLGraphics.kext",
                            "AppleIntelICLLPGraphicsFramebuffer.kext",
                            "AppleIntelKBLGraphics.kext",
                            "AppleIntelKBLGraphicsFramebuffer.kext",
                            "AppleIntelSKLGraphics.kext",
                            "AppleIntelSKLGraphicsFramebuffer.kext",
                            "AppleIntelFramebufferAzul.kext",
                            "AppleIntelFramebufferCapri.kext",
                            "AppleParavirtGPU.kext",
                            "GeForce.kext",
                            "IOAcceleratorFamily2.kext",
                            "IOGPUFamily.kext",
                            "AppleAfterburner.kext",
                        ],
                    },
                    "Install Non-Root": {
                        "/Library/Application Support/SkyLightPlugins": {
                            **({ "DropboxHack.dylib":    "SkyLightPlugins" } if self.os_major >= os_data.os_data.monterey else {}),
                            **({ "DropboxHack.txt":      "SkyLightPlugins" } if self.os_major >= os_data.os_data.monterey else {}),
                        },
                    },
                    "Processes": {
                        # 'When Space Allows' option introduced in 12.4 (XNU 21.5)
                        **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist ShowDate -int 1": True } if self.os_float >= self.macOS_12_4 else {}),
                        "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist InternalDebugUseGPUProcessForCanvasRenderingEnabled -bool false": True,
                        "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist WebKitExperimentalUseGPUProcessForCanvasRenderingEnabled -bool false": True,
                        **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist WebKitPreferences.acceleratedDrawingEnabled -bool false": True} if self.os_major >= os_data.os_data.sonoma else {}),
                        **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist NSEnableAppKitMenus -bool false": True} if self.os_major >= os_data.os_data.sonoma else {}),
                        **({"/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist NSZoomButtonShowMenu -bool false": True} if self.os_major >= os_data.os_data.sonoma else {}),
                    },
                },
                "Non-Metal IOAccelerator Common": {
                    # TeraScale 2 and Nvidia Web Drivers broke in Mojave due to mismatched structs in
                    # the IOAccelerator stack
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": self.non_metal_os_support[-1],
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "IOAcceleratorFamily2.kext":     "10.13.6",
                            "IOSurface.kext":                "10.14.6",
                        },
                        "/System/Library/Frameworks": {
                            "IOSurface.framework": f"10.14.6-{self.os_major}",
                            "OpenCL.framework":     "10.13.6",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "GPUSupport.framework":     "10.13.6",
                            "IOAccelerator.framework": f"10.13.6-{self.os_major}",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            "AppleCameraInterface.kext"
                        ],
                    },
                },

                "Non-Metal CoreDisplay Common": {
                    # Nvidia Web Drivers require an older build of CoreDisplay
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": self.non_metal_os_support[-1],
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "CoreDisplay.framework": f"10.13.6-{self.os_major}",
                        },
                    },
                },

                "Non-Metal Enforcement": {
                    # Forces Metal kexts from High Sierra to run in the fallback non-Metal mode
                    # Verified functional with HD4000 and Iris Plus 655
                    # Only used for internal development purposes, not suitable for end users

                    # Note: Metal kexts in High Sierra rely on IOAccelerator, thus 'Non-Metal IOAccelerator Common'
                    # is needed for proper linking
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": self.non_metal_os_support[-1],
                            "OS Minor": 99
                        },
                    },
                    "Processes": {
                        "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useMetal -boolean no": True,
                        "/usr/bin/defaults write /Library/Preferences/com.apple.CoreDisplay useIOP -boolean no":   True,
                    },
                },

                "Revert Non-Metal ColorSync Workaround": {
                    # Old patch for ColorSync in Ventura on HD3000s
                    # Proper solution has been integrated into QuartzCore
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 99
                        },
                    },
                    "Remove": {
                        "/System/Library/Frameworks/ColorSync.framework/Versions/A": [
                            "ColorSync",
                            "ColorSyncOld.dylib",
                        ],
                    },
                },

                # AMD GCN and Nvidia Kepler require Metal Downgrade in Ventura
                # The patches are required due to struct issues in the Metal stack
                # - AMD GCN will break on BronzeMtlDevice
                # - See Nvidia Kepler patchset for more info
                "Metal Common": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "Metal.framework":                   "12.5",
                            "MetalPerformanceShaders.framework": "12.5",
                        },
                    },
                },

                # Temporary work-around for Kepler GPUs on Ventura
                # We removed the reliance on Metal.framework downgrade, however the new Kepler
                # patchset breaks with the old Metal. Thus we need to ensure stock variant is used
                # Remove this when OCLP is merged onto mainline
                "Revert Metal Downgrade": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 99
                        },
                    },
                    "Remove": {
                        "/System/Library/Frameworks/Metal.framework/Versions/A/": [
                            "Metal",
                            "MetalOld.dylib",
                        ],
                        "/System/Library/Frameworks/MetalPerformanceShaders.framework/Versions/A/Frameworks/MPSCore.framework/Versions/A": [
                            "MPSCore",
                        ],
                    },
                },

                # Monterey has a WebKit sandboxing issue where many UI elements fail to render
                # This patch simple replaces the sandbox profile with one supporting our GPUs
                # Note: Neither Big Sur nor Ventura have this issue
                "WebKit Monterey Common": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "WebKit.framework":  "11.6"
                        },
                    },
                    "Install Non-Root": {
                        "/Library/Apple/System/Library/StagedFrameworks/Safari": {
                            "WebKit.framework":  "11.6"
                        },
                    },
                },

                # Intel Ivy Bridge, Haswell and Nvidia Kepler are Metal 3802-based GPUs
                # Due to this, we need to re-add 3802 compiler support to the Metal stack
                "Metal 3802 Common": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "Metal.framework": f"12.5-3802-{self.os_major}",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "MTLCompiler.framework": "12.5-3802",
                            "GPUCompiler.framework": "12.5-3802",
                        },
                        "/System/Library/Sandbox/Profiles": {
                            "com.apple.mtlcompilerservice.sb": "12.5-3802",
                        }
                    },
                },

                # Support for 3802 GPUs were broken with 13.3+
                # Downgrades 31001 stack to 13.2.1, however nukes AMFI support
                "Metal 3802 Common Extended": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 4 # 13.3
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "Metal.framework": f"13.2.1-{self.os_major}",
                            **({  "CoreImage.framework": "14.0 Beta 3" } if self.os_major >= os_data.os_data.sonoma else {}),
                        },
                        "/System/Library/PrivateFrameworks": {
                            **({  "MTLCompiler.framework": "13.2.1" } if self.os_major == os_data.os_data.ventura else {}),
                            **({  "GPUCompiler.framework": "13.2.1" } if self.os_major == os_data.os_data.ventura else {}),
                            "RenderBox.framework": "13.2.1-3802"      if self.os_major == os_data.os_data.ventura else "14.0-3802",

                            # More issues for 3802, now with 14.2 Beta 2+...
                            # If there is a god, they clearly despise us and legacy Macs.
                            **({  "MTLCompiler.framework": "14.2 Beta 1" } if self.os_float >= self.macOS_14_2 else {}),
                            **({  "GPUCompiler.framework": "14.2 Beta 1" } if self.os_float >= self.macOS_14_2 else {}),
                        },
                    },
                },

                # Primarily for AMD GCN GPUs
                "Revert GVA Downgrade": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Remove": {
                        "/System/Library/PrivateFrameworks/AppleGVA.framework/Versions/A/": [
                            "AppleGVA",
                        ],
                        "/System/Library/PrivateFrameworks/AppleGVACore.framework/Versions/A/": [
                            "AppleGVACore",
                        ],
                    },
                },

                # For GPUs last natively supported in Catalina/Big Sur
                # Restores DRM support
                "Catalina GVA": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/PrivateFrameworks": {
                            "AppleGVA.framework":     "11.7.10",
                            "AppleGVACore.framework": "11.7.10",
                        },
                    },
                },

                # For GPUs last natively supported in Monterey
                # Restores DRM support
                "Monterey GVA": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/PrivateFrameworks": {
                            "AppleGVA.framework":     "12.5",
                            "AppleGVACore.framework": "12.5",
                        },
                    },
                },

                "High Sierra GVA": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/PrivateFrameworks": {
                            "AppleGVA.framework":     "10.13.6",
                            "AppleGVACore.framework": "10.15.7",
                        },
                    },
                },

                "Big Sur OpenCL": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "OpenCL.framework": "11.6",
                        },
                    },
                },

                "Monterey OpenCL": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "OpenCL.framework": "12.5",
                        },
                    },
                },

                # In Ventura, Apple added AVX2.0 code to AMD's OpenCL/GL compilers
                "AMD OpenCL": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "OpenCL.framework": "12.5 non-AVX2.0",
                            "OpenGL.framework": "12.5 non-AVX2.0",
                        },
                    },
                },

                "Nvidia Tesla": {
                    "Display Name": "Graphics: Nvidia Tesla",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "GeForceGA.bundle":            "10.13.6",
                            "GeForceTesla.kext":           "10.13.6",
                            "GeForceTeslaGLDriver.bundle": "10.13.6",
                            "GeForceTeslaVADriver.bundle": "10.13.6",
                            "NVDANV50HalTesla.kext":       "10.13.6",
                            "NVDAResmanTesla.kext":        "10.13.6",
                            # Apple dropped NVDAStartup in 12.0 Beta 7 (XNU 21.1)
                            **({ "NVDAStartup.kext":       "12.0 Beta 6" } if self.os_float >= self.macOS_12_0_B7 else {})
                        },
                    },
                },
                "Nvidia Kepler": {
                    "Display Name": "Graphics: Nvidia Kepler",
                    "OS Support": {
                        "Minimum OS Support": {
                            # 12.0 beta 7 (XNU 21.1)
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 1
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "GeForce.kext":            self.__resolve_kepler_geforce_framebuffers(),
                            "NVDAGF100Hal.kext":       "12.0 Beta 6",
                            "NVDAGK100Hal.kext":       "12.0 Beta 6",
                            "NVDAResman.kext":         "12.0 Beta 6",
                            "NVDAStartup.kext":        "12.0 Beta 6",
                            "GeForceAIRPlugin.bundle": "11.0 Beta 3",
                            "GeForceGLDriver.bundle":  "11.0 Beta 3",
                            "GeForceMTLDriver.bundle": "11.0 Beta 3" if self.os_major <= os_data.os_data.monterey else f"11.0 Beta 3-22",
                            "GeForceVADriver.bundle":  "12.0 Beta 6",
                        },
                        "/System/Library/Frameworks": {
                            # XNU 21.6 (macOS 12.5)
                            **({ "Metal.framework": "12.5 Beta 2"} if (self.os_float >= self.macOS_12_5 and self.os_major < os_data.os_data.ventura) else {}),
                        },
                        "/System/Library/PrivateFrameworks": {
                            "GPUCompiler.framework": "11.6",
                        },
                    },
                },
                "Nvidia Web Drivers": {
                    "Display Name": "Graphics: Nvidia Web Drivers",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "GeForceAIRPluginWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                            "GeForceGLDriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",
                            "GeForceMTLDriverWeb.bundle":     "WebDriver-387.10.10.10.40.140",
                            "GeForceVADriverWeb.bundle":      "WebDriver-387.10.10.10.40.140",

                            # Tesla-only files
                            "GeForceTeslaGAWeb.bundle":       "WebDriver-387.10.10.10.40.140",
                            "GeForceTeslaGLDriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                            "GeForceTeslaVADriverWeb.bundle": "WebDriver-387.10.10.10.40.140",
                        },
                        "/System/Library/PrivateFrameworks": {
                            # Restore OpenCL by adding missing compiler files
                            **({ "GPUCompiler.framework": "11.6"} if self.os_major >= os_data.os_data.monterey else {}),
                        },
                    },
                    "Install Non-Root": {
                        "/Library/Extensions": {
                            "GeForceWeb.kext":                "WebDriver-387.10.10.10.40.140",
                            "NVDAGF100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                            "NVDAGK100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                            "NVDAGM100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                            "NVDAGP100HalWeb.kext":           "WebDriver-387.10.10.10.40.140",
                            "NVDAResmanWeb.kext":             "WebDriver-387.10.10.10.40.140",
                            "NVDAStartupWeb.kext":            "WebDriver-387.10.10.10.40.140",

                            # Tesla-only files
                            "GeForceTeslaWeb.kext":           "WebDriver-387.10.10.10.40.140",
                            "NVDANV50HalTeslaWeb.kext":       "WebDriver-387.10.10.10.40.140",
                            "NVDAResmanTeslaWeb.kext":        "WebDriver-387.10.10.10.40.140",
                        },

                        # Disabled due to issues with Pref pane stripping 'nvda_drv' NVRAM
                        # variables
                        # "/Library/PreferencePanes": {
                        #     "NVIDIA Driver Manager.prefPane": "WebDriver-387.10.10.10.40.140",
                        # },
                        #  "/Library/LaunchAgents": {
                        #     "com.nvidia.nvagent.plist":       "WebDriver-387.10.10.10.40.140",
                        # },
                        # "/Library/LaunchDaemons": {
                        #     "com.nvidia.nvroothelper.plist":  "WebDriver-387.10.10.10.40.140",
                        # },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            # Due to how late the Auxiliary cache loads, NVDAStartup will match first and then the Web Driver kexts.
                            # This has no effect for Maxwell and Pascal, however for development purposes, Tesla and Kepler are partially supported.
                            "NVDAStartup.kext",
                        ],
                    },
                },
                "AMD TeraScale Common": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMDFramebuffer.kext":           "10.13.6",
                            "AMDLegacyFramebuffer.kext":     "10.13.6",
                            "AMDLegacySupport.kext":         "10.13.6",
                            "AMDShared.bundle":              "10.13.6",
                            "AMDSupport.kext":               "10.13.6",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            "AMD7000Controller.kext",
                            "AMD8000Controller.kext",
                            "AMD9000Controller.kext",
                            "AMD9500Controller.kext",
                            "AMD10000Controller.kext",
                        ],
                    },
                },

                "AMD TeraScale 1": {
                    "Display Name": "Graphics: AMD TeraScale 1",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMD2400Controller.kext":        "10.13.6",
                            "AMD2600Controller.kext":        "10.13.6",
                            "AMD3800Controller.kext":        "10.13.6",
                            "AMD4600Controller.kext":        "10.13.6",
                            "AMD4800Controller.kext":        "10.13.6",
                            "ATIRadeonX2000.kext":           "10.13.6" if self.os_major < os_data.os_data.ventura else "10.13.6 TS1",
                            "ATIRadeonX2000GA.plugin":       "10.13.6",
                            "ATIRadeonX2000GLDriver.bundle": "10.13.6",
                            "ATIRadeonX2000VADriver.bundle": "10.13.6",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            # Following removals are a work around for 0.4.3 and older root patches
                            # Previously TS1 and TS2 patch sets were shared, now they're split off
                            # Due to this, updating to 0.4.4 or newer can break kmutil linking
                            "AMD5000Controller.kext",
                            "AMD6000Controller.kext",
                            "AMDRadeonVADriver.bundle",
                            "AMDRadeonVADriver2.bundle",
                            "AMDRadeonX3000.kext",
                            "AMDRadeonX3000GLDriver.bundle",
                        ],
                    },
                },
                "AMD TeraScale 2": {
                    "Display Name": "Graphics: AMD TeraScale 2",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMD5000Controller.kext":        "10.13.6",
                            "AMD6000Controller.kext":        "10.13.6",
                            "AMDRadeonVADriver.bundle":      "10.13.6",
                            "AMDRadeonVADriver2.bundle":     "10.13.6",
                            "AMDRadeonX3000.kext":           "10.13.6",
                            "AMDRadeonX3000GLDriver.bundle": "10.13.6",
                        },
                    },
                },
                "AMD Legacy GCN": {
                    "Display Name": "Graphics: AMD Legacy GCN",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMD7000Controller.kext":        "12.5",
                            "AMD8000Controller.kext":        "12.5",
                            "AMD9000Controller.kext":        "12.5",
                            "AMD9500Controller.kext":        "12.5",
                            "AMD10000Controller.kext":       "12.5",
                            "AMDRadeonX4000.kext":           self.__resolve_monterey_framebuffers(),
                            "AMDRadeonX4000HWServices.kext": "12.5",
                            "AMDFramebuffer.kext":           "12.5" if self.os_float < self.macOS_13_3 else "12.5-GCN",
                            "AMDSupport.kext":               "12.5",

                            "AMDRadeonVADriver.bundle":      "12.5",
                            "AMDRadeonVADriver2.bundle":     "12.5",
                            "AMDRadeonX4000GLDriver.bundle": "12.5",
                            "AMDMTLBronzeDriver.bundle":     "12.5",
                            "AMDShared.bundle":              "12.5",
                        },
                    },
                },

                # For MacBookPro14,3 (and other AMD dGPUs that no longer function in Sonoma)
                # iMac18,2/3 still function with the generic framebuffer, however if issues arise
                # we'll downgrade them as well.
                "AMD Legacy GCN v2": {
                    "Display Name": "Graphics: AMD Legacy GCN (2017)",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sonoma,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMD9500Controller.kext":        "13.5.2",
                            "AMD10000Controller.kext":       "13.5.2",
                            "AMDRadeonX4000.kext":           "13.5.2",
                            "AMDRadeonX4000HWServices.kext": "13.5.2",
                            "AMDFramebuffer.kext":           "13.5.2",
                            "AMDSupport.kext":               "13.5.2",

                            "AMDRadeonVADriver.bundle":      "13.5.2",
                            "AMDRadeonVADriver2.bundle":     "13.5.2",
                            "AMDRadeonX4000GLDriver.bundle": "13.5.2",
                            "AMDMTLBronzeDriver.bundle":     "13.5.2",
                            "AMDShared.bundle":              "13.5.2",
                        },
                    },
                },

                # Used only for AMD Polaris with host lacking AVX2.0
                # Note missing framebuffers are not restored (ex. 'ATY,Berbice')
                "AMD Legacy Polaris": {
                    "Display Name": "Graphics: AMD Legacy Polaris",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMDRadeonX4000.kext":           self.__resolve_monterey_framebuffers(),
                            "AMDRadeonX4000HWServices.kext": "12.5",

                            "AMDRadeonVADriver2.bundle":     "12.5",
                            "AMDRadeonX4000GLDriver.bundle": "12.5",
                            "AMDMTLBronzeDriver.bundle":     "12.5",
                            "AMDShared.bundle":              "12.5",
                        },
                    },
                },
                "AMD Legacy Vega": {
                    "Display Name": "Graphics: AMD Legacy Vega",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMDRadeonX5000.kext":            self.__resolve_monterey_framebuffers(),

                            "AMDRadeonVADriver2.bundle":      "12.5",
                            "AMDRadeonX5000GLDriver.bundle":  "12.5",
                            "AMDRadeonX5000MTLDriver.bundle": "12.5",
                            "AMDRadeonX5000Shared.bundle":    "12.5",

                            "AMDShared.bundle":               "12.5",
                        },
                    },
                },
                # Support mixed legacy and modern AMD GPUs
                # Specifically systems using AMD GCN 1-3 and Vega (ex. MacPro6,1 with eGPU)
                # Assume 'AMD Legacy GCN' patchset is installed alongside this
                "AMD Legacy Vega Extended": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AMDRadeonX5000HWServices.kext": "12.5",
                        },
                    },
                },
                "Intel Ironlake": {
                    "Display Name": "Graphics: Intel Ironlake",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelHDGraphics.kext":           "10.13.6",
                            "AppleIntelHDGraphicsFB.kext":         "10.13.6",
                            "AppleIntelHDGraphicsGA.plugin":       "10.13.6",
                            "AppleIntelHDGraphicsGLDriver.bundle": "10.13.6",
                            "AppleIntelHDGraphicsVADriver.bundle": "10.13.6",
                        },
                    },
                },
                "Intel Sandy Bridge": {
                    "Display Name": "Graphics: Intel Sandy Bridge",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelHD3000Graphics.kext":           "10.13.6",
                            "AppleIntelHD3000GraphicsGA.plugin":       "10.13.6",
                            "AppleIntelHD3000GraphicsGLDriver.bundle": "10.13.6",
                            "AppleIntelHD3000GraphicsVADriver.bundle": "10.13.6",
                            "AppleIntelSNBGraphicsFB.kext":            "10.13.6",
                            "AppleIntelSNBVA.bundle":                  "10.13.6",
                        },
                    },
                },
                "Intel Ivy Bridge": {
                    "Display Name": "Graphics: Intel Ivy Bridge",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelHD4000GraphicsGLDriver.bundle":  "11.7.10",
                            "AppleIntelHD4000GraphicsMTLDriver.bundle": "11.7.10" if self.os_major < os_data.os_data.ventura else "11.7.10-22",
                            "AppleIntelHD4000GraphicsVADriver.bundle":  "11.7.10",
                            "AppleIntelFramebufferCapri.kext":          self.__resolve_ivy_bridge_framebuffers(),
                            "AppleIntelHD4000Graphics.kext":            self.__resolve_ivy_bridge_framebuffers(),
                            "AppleIntelIVBVA.bundle":                   "11.7.10",
                            "AppleIntelGraphicsShared.bundle":          "11.7.10", # libIGIL-Metal.dylib pulled from 11.0 Beta 6
                        },
                    },
                },
                "Intel Haswell": {
                    "Display Name": "Graphics: Intel Haswell",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelFramebufferAzul.kext":           self.__resolve_monterey_framebuffers(),
                            "AppleIntelHD5000Graphics.kext":            self.__resolve_monterey_framebuffers(),
                            "AppleIntelHD5000GraphicsGLDriver.bundle":  "12.5",
                            "AppleIntelHD5000GraphicsMTLDriver.bundle": "12.5",
                            "AppleIntelHD5000GraphicsVADriver.bundle":  "12.5",
                            "AppleIntelHSWVA.bundle":                   "12.5",
                            "AppleIntelGraphicsShared.bundle":          "12.5",
                        },
                    },
                },
                "Intel Broadwell": {
                    "Display Name": "Graphics: Intel Broadwell",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelBDWGraphics.kext":            self.__resolve_monterey_framebuffers(),
                            "AppleIntelBDWGraphicsFramebuffer.kext": self.__resolve_monterey_framebuffers(),
                            "AppleIntelBDWGraphicsGLDriver.bundle":  "12.5",
                            "AppleIntelBDWGraphicsMTLDriver.bundle": "12.5-22",
                            "AppleIntelBDWGraphicsVADriver.bundle":  "12.5",
                            "AppleIntelBDWGraphicsVAME.bundle":      "12.5",
                            "AppleIntelGraphicsShared.bundle":       "12.5",
                        },
                    },
                },
                "Intel Skylake": {
                    "Display Name": "Graphics: Intel Skylake",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleIntelSKLGraphics.kext":            self.__resolve_monterey_framebuffers(),
                            "AppleIntelSKLGraphicsFramebuffer.kext": self.__resolve_monterey_framebuffers(),
                            "AppleIntelSKLGraphicsGLDriver.bundle":  "12.5",
                            "AppleIntelSKLGraphicsMTLDriver.bundle": "12.5",
                            "AppleIntelSKLGraphicsVADriver.bundle":  "12.5",
                            "AppleIntelSKLGraphicsVAME.bundle":      "12.5",
                            "AppleIntelGraphicsShared.bundle":       "12.5",
                        },
                    },
                },
            },
            "Audio": {
                "Legacy Realtek": {
                    "Display Name": "Audio: Legacy Realtek",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sierra,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    # For iMac7,1 and iMac8,1 units with legacy Realtek HD Audio
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleHDA.kext":      "10.11.6",
                            "IOAudioFamily.kext": "10.11.6",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            "AppleVirtIO.kext",
                            "AppleVirtualGraphics.kext",
                            "AppleVirtualPlatform.kext",
                            "ApplePVPanic.kext",
                            "AppleVirtIOStorage.kext",
                        ],
                    },
                },
                # For Mac Pros with non-UGA/GOP GPUs
                "Legacy Non-GOP": {
                    "Display Name": "Audio: Legacy non-GOP",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.mojave,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleHDA.kext": "10.13.6",
                        },
                    },
                },
            },
            "Networking": {
                "Legacy Wireless": {
                    "Display Name": "Networking: Legacy Wireless",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.monterey,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/usr/libexec": {
                            "airportd": "11.7.10" if self.affected_by_cve_2024_23227 is False else "11.7.10-Sandbox",
                        },
                        "/System/Library/CoreServices": {
                            "WiFiAgent.app": "11.7.10",
                        },
                    },
                    "Install Non-Root": {
                        "/Library/Application Support/SkyLightPlugins": {
                            **({ "CoreWLAN.dylib": "SkyLightPlugins" } if self.os_major == os_data.os_data.monterey else {}),
                            **({ "CoreWLAN.txt": "SkyLightPlugins" } if self.os_major == os_data.os_data.monterey else {}),
                        },
                    },
                },
                "Legacy Wireless Extended": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/usr/libexec": {
                            "wps":      "12.7.2",
                            "wifip2pd": "12.7.2",
                        },
                        "/System/Library/Frameworks": {
                            "CoreWLAN.framework": "12.7.2",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "CoreWiFi.framework": "12.7.2",
                            "IO80211.framework":  "12.7.2",
                            "WiFiPeerToPeer.framework":  "12.7.2",
                        },
                    },
                },
                # May lord have mercy on our souls
                # Applicable for BCM943324, BCM94331, BCM94360, BCM943602
                "Modern Wireless": {
                    "Display Name": "Networking: Modern Wireless",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sonoma,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/usr/libexec": {
                            "airportd":       "13.6.5",
                            "wifip2pd":       "13.6.5",
                        },
                        "/System/Library/Frameworks": {
                            "CoreWLAN.framework": f"13.6.5-{self.os_major}",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "CoreWiFi.framework":       f"13.6.5-{self.os_major}",
                            "IO80211.framework":        f"13.6.5-{self.os_major}",
                            "WiFiPeerToPeer.framework": f"13.6.5-{self.os_major}",
                        },
                    },
                },
            },
            "Brightness": {
                "Legacy Backlight Control": {
                    "Display Name": "Brightness: Legacy Backlight Control",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.high_sierra,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "AppleBacklight.kext":       "10.12.6",
                            "AppleBacklightExpert.kext": "10.12.6",
                        },
                        "/System/Library/PrivateFrameworks": {
                            "DisplayServices.framework": "10.12.6",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                            "AGDCBacklightControl.kext",
                        ],
                    },
                },
            },
            "Miscellaneous": {
                "Legacy GMUX": {
                    "Display Name": "Miscellaneous: Legacy GMUX",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.high_sierra,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": {
                            "AppleMuxControl.kext": "10.12.6",
                        },
                    },
                    "Remove": {
                        "/System/Library/Extensions": [
                            "AppleBacklight.kext",
                        ],
                        "/System/Library/Extensions/AppleGraphicsControl.kext/Contents/PlugIns": [
                            "AGDCBacklightControl.kext",
                            "AppleMuxControl.kext",
                        ],
                    },
                },
                "Legacy Keyboard Backlight": {
                    "Display Name": "Miscellaneous: Legacy Keyboard Backlight",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": self.non_metal_os_support[0],
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": self.non_metal_os_support[-1],
                            "OS Minor": 99
                        },
                    },
                    "Processes": {
                        "/usr/bin/defaults write /Library/Preferences/.GlobalPreferences.plist Moraea_BacklightHack -bool true": True,
                    },
                },
                "Legacy USB 1.1": {
                    "Display Name": "Miscellaneous: Legacy USB 1.1",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.ventura,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions": {
                            "IOUSBHostFamily.kext": "12.6.2" if self.os_float < self.macOS_14_4 else "12.6.2-23.4",
                        },
                    },
                },
                # Injection of UHCI/OHCI causes a panic on 14.1+
                "Legacy USB 1.1 Extended": {
                    "Display Name": "",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sonoma,
                            "OS Minor": 1 # macOS 14.1 (XNU 23.1)
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Extensions/IOUSBHostFamily.kext/Contents/PlugIns": {
                            "AppleUSBOHCI.kext":    "12.6.2-USB",
                            "AppleUSBOHCIPCI.kext": "12.6.2-USB",
                            "AppleUSBUHCI.kext":    "12.6.2-USB",
                            "AppleUSBUHCIPCI.kext": "12.6.2-USB",
                        },
                    },
                },
                # With macOS 14.1, daemon won't load if not on root volume
                "PCIe FaceTime Camera": {
                    "Display Name": "Miscellaneous: PCIe FaceTime Camera",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sonoma,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks/CoreMediaIO.framework/Versions/A/Resources": {
                            "AppleCamera.plugin":  "14.0 Beta 1"
                        },
                        "/System/Library/LaunchDaemons": {
                            "com.apple.cmio.AppleCameraAssistant.plist":  "14.0 Beta 1"
                        },
                    },
                    "Remove Non-Root": {
                        "/Library/CoreMediaIO/Plug-Ins/DAL": [
                            "AppleCamera.plugin"
                        ],
                        "/Library/LaunchDaemons": [
                            "com.apple.cmio.AppleCameraAssistant.plist"
                        ],
                    }
                },
                "T1 Security Chip": {
                    "Display Name": "Miscellaneous: T1 Security Chip",
                    "OS Support": {
                        "Minimum OS Support": {
                            "OS Major": os_data.os_data.sonoma,
                            "OS Minor": 0
                        },
                        "Maximum OS Support": {
                            "OS Major": os_data.os_data.max_os,
                            "OS Minor": 99
                        },
                    },
                    "Install": {
                        "/System/Library/Frameworks": {
                            "LocalAuthentication.framework": f"13.6-{self.os_major}"  # Required for Password Authentication (SharedUtils.framework)
                        },
                        "/System/Library/PrivateFrameworks": {
                            "EmbeddedOSInstall.framework": "13.6"  # Required for biometrickitd
                        },
                        # Required for Apple Pay
                        "/usr/lib": {
                            "libNFC_Comet.dylib":          "13.6",
                            "libNFC_HAL.dylib":            "13.6",

                            "libnfshared.dylib":           "13.6",
                            "libnfshared.dylibOld.dylib":  "13.6",
                            "libnfstorage.dylib":          "13.6",
                            "libnfrestore.dylib":          "13.6",

                            "libPN548_API.dylib":          "13.6"
                        },
                        "/usr/libexec": {
                            "biometrickitd":        "13.6",  # Required for Touch ID
                            "nfcd":               "13.6",    # Required for Apple Pay
                            "nfrestore_service":  "13.6",    # Required for Apple Pay
                        },
                        "/usr/standalone/firmware/nfrestore/firmware/fw": {
                            "PN549_FW_02_01_5A_rev88207.bin":         "13.6",
                            "SN100V_FW_A3_01_01_81_rev127208.bin":    "13.6",
                            "SN200V_FW_B1_02_01_86_rev127266.bin":    "13.6",
                            "SN300V_FW_B0_02_01_22_rev129172.bin":    "13.6",
                        }
                    },
                },
            },
        }

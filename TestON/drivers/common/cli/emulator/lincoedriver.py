#!/usr/bin/env python

"""
Copyright 2014 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.



This driver handles the optical switch emulator linc-oe.

Please follow the coding style demonstrated by existing
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

    andrew@onlab.us
    shreya@onlab.us

OCT 20 2014
"""

import pexpect
import sys
from drivers.common.cli.emulatordriver import Emulator


class LincOEDriver( Emulator ):

    """
    LincOEDriver class will handle all emulator functions
    """
    def __init__( self ):
        super( LincOEDriver, self ).__init__()
        self.handle = self
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0

    def connect( self, **connectargs ):
        """
        Create ssh handle for Linc-OE cli
        """

        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]
        self.handle = \
            super( LincOEDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

        self.sshHandle = self.handle

        if self.handle:
            main.log.info( "Handle successfully created" )
            self.home = "~/linc-oe"

            self.handle.sendline( "cd " + self.home )
            self.handle.expect( "oe$" )

            print "handle = ", self.handle.before

            return main.TRUE
        else:
            main.log.error( self.name +
                            ": Connection failed to the host " +
                            self.user_name + "@" + self.ip_address )
            main.log.error( self.name +
                            ": Failed to connect to Linc-OE" )
            return main.FALSE

    def startConsole( self ):
        import time
        main.log.info(
            self.name +
            ": Starting Linc-OE CLI.. This may take a while" )
        time.sleep( 30 )
        self.handle.sendline( "sudo ./rel/linc/bin/linc console" )
        j = self.handle.expect( [ "linc@", pexpect.EOF, pexpect.TIMEOUT ] )
        startResult = self.handle.before
        if j == 0:
            main.log.info( "Linc-OE CLI started" )
            return main.TRUE
        else:
            main.log.error(
                self.name +
                ": Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            main.log.error( self.name +
                            ": Failed to connect to Linc-OE" )
            return main.FALSE

    def build( self ):
        """
        Build Linc-OE with the specified settings
        """
        try:
            self.handle.sendline( "make rel" )
            i = self.handle.expect( [
                "ERROR",
                self.prompt ] )

            if i == 0:
                self.handle.sendline( "sudo pkill -9 epmd" )
                self.handle.sendline( "make rel" )
                self.handle.expect( self.prompt )

                handle = self.handle.before
                return handle

            else:
                return main.TRUE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setInterfaceUp( self, intfs ):
        """
        Specify interface to bring up.
        When Linc-OE is started, tap interfaces should
        be created. They must be brought up manually
        """
        try:
            self.handle.sendline( "ifconfig " + str( intfs ) + " up" )
            self.handle.expect( "linc@" )

            handle = self.handle.before

            return handle

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startSwitch( self, swId ):
        """
        Start a logical switch using switch id
        """
        try:
            self.handle.sendline( "linc:start_switch(" + str( swId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def stopSwitch( self, swId ):
        """
        Stop a logical switch using switch id
        """
        try:
            self.handle.sendline( "linc:stop_switch(" + str( swId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getDatapathId( self, swId ):
        """
        Get datapath id of a specific switch by switch id
        """
        try:
            self.handle.sendline( "linc_logic:get_datapath_id(" +
                                  str( swId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def attachLincOESession( self ):
        """
            Since executing opticalTest.py will give you mininet
            prompt, you would at some point require to get onto
            console of LincOE ((linc@onosTestBench)1>) to execute
            commands like bring a optical port up or down on a ROADM
            You can attach to console of Linc-OE session by a cmd:
            sudo ~/linc-oe/rel/linc/bin/linc attach
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "sudo ~/linc-oe/rel/linc/bin/linc attach" )
            self.handle.expect( ">" )
            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def listPorts( self, swId ):
        """
        List all ports of a switch by switch id
        """
        try:
            self.handle.sendline( "linc:ports(" + str( swId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def portUp( self, swId, ptId ):
        """
        Bring port up using switch id and port id
        """
        try:
            self.handle.sendline( "linc:port_up(" +
                                  str( swId ) + ", " + str( ptId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def portDown( self, swId, ptId ):
        """
        Bring port down using switch id and port id
        """
        try:
            self.handle.sendline( "linc:port_down(" +
                                  str( swId ) + ", " + str( ptId ) + ")." )
            self.handle.expect( "linc@" )

            handle = self.handle.before

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def stopLincOEConsole( self ):
        """
        This function is only used for packet optical testing
        Send disconnect prompt to Linc-OE CLI
        ( CTRL+C ) and kill the linc process
        """
        try:
            cmd = "pgrep -f linc"
            self.handle.sendline( "pgrep -f linc" )
            self.handle.expect( "linc" )
            print "stophandle = ", self.handle.before
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )

    def disconnect( self ):
        """
        Send disconnect prompt to Linc-OE CLI
        ( CTRL+C ) and kill the linc process
        """
        try:
            # Send CTRL+C twice to exit CLI
            self.handle.send( "\x03" )
            self.handle.send( "\x03" )
            self.handle.expect( self.prompt )
            handle1 = self.handle.before
            cmd = "pgrep -f linc"
            self.handle.sendline( cmd )
            self.handle.expect( self.prompt )
            handle2 = self.handle.before
            main.log.info( "pid's = " + handle2 )
            cmd = "sudo kill -9 `pgrep -f linc`"
            self.handle.sendline( cmd )
            self.handle.expect( self.prompt )
            # Close the ssh connection
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "exit" )
            self.handle.expect( "closed" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

if __name__ != "__main__":
    import sys
    sys.modules[ __name__ ] = LincOEDriver()

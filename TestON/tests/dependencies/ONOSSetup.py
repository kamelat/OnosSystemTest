
import time
import re
import imp

class ONOSSetup:
    main = None
    def __init__( self ):
        self.default = ''
    def envSetupDescription ( self ):
        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        main.caseExplanation = "For loading from params file, and pull" + \
                               " and build the latest ONOS package"
        main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )

    def gitPulling( self ):
        main.case( "Pull onos branch and build onos on Teststation." )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        if gitPull == 'True':
            main.step( "Git Checkout ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.gitCheckout( branch=gitBranch )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully checkout onos branch.",
                                     onfail="Failed to checkout onos branch. Exiting test..." )
            if not stepResult: main.exit()

            main.step( "Git Pull on ONOS branch:" + gitBranch )
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully pull onos. ",
                                     onfail="Failed to pull onos. Exiting test ..." )
            if not stepResult: main.exit()

        else:
            main.log.info( "Skipped git checkout and pull as they are disabled in params file" )

        return main.TRUE

    def setRest( self, hasRest, i ):
        if hasRest:
            main.RESTs.append( getattr( main, "ONOSrest" + str( i ) ) )

    def setNode( self, hasNode, i ):
        if hasNode:
            main.nodes.append( getattr( main, 'ONOS' + str(i)) )

    def setCli( self, hasCli, i ):
        if hasCli:
            main.CLIs.append( getattr ( main, "ONOScli" + str( i ) ) )

    def getNumNode( self, hasCli, hasNode, hasRest ):
        if hasCli:
            return len( main.CLIs )
        if hasNode:
            return len( main.nodes )
        if hasRest:
            return len( main.RESTs )

    def envSetup ( self, hasMultiNodeRounds=False, hasRest=False, hasNode=False,
                   hasCli=True, specificIp="", includeGitPull=True, makeMaxNodes=True ):
        if includeGitPull :
            self.gitPulling()
        if main.ONOSbench.maxNodes:
            main.maxNodes = int( main.ONOSbench.maxNodes )
        else:
            main.maxNodes = 0
        main.cellData = {}  # For creating cell file
        if hasCli:
            main.CLIs = []
        if hasRest:
            main.RESTs = []
        if hasNode:
            main.nodes = []
        main.ONOSip = []  # List of IPs of active ONOS nodes. CASE 2

        if specificIp == "":
            if makeMaxNodes:
                main.ONOSip = main.ONOSbench.getOnosIps()
        else:
            main.ONOSip.append( specificIp )

        # Assigning ONOS cli handles to a list
        try:
            for i in range( 1, ( main.maxNodes if makeMaxNodes else main.numCtrls ) + 1 ):
                self.setCli( hasCli, i )
                self.setRest( hasRest, i )
                self.setNode( hasNode, i )
                if not makeMaxNodes:
                    main.ONOSip.append( main.ONOSbench.getOnosIps()[ i - 1 ] )
        except AttributeError:
            numNode = self.getNumNode( hasCli, hasNode, hasRest )
            main.log.warn( "A " + str( main.maxNodes ) + " node cluster " +
                          "was defined in env variables, but only " +
                          str( numNode ) +
                          " nodes were defined in the .topo file. " +
                          "Using " + str( numNode ) +
                          " nodes for the test." )
            main.maxNodes = numNode

        main.log.debug( "Found ONOS ips: {}".format( main.ONOSip ) )
        if ( not hasCli or main.CLIs ) and ( not hasRest or main.RESTs )\
                and ( not hasNode or main.nodes ):
            return main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
            return main.FALSE

    def envSetupException ( self, e ):
        main.log.exception( e )
        main.cleanup()
        main.exit()

    def evnSetupConclusion ( self, stepResult ):
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

        main.commit = main.ONOSbench.getVersion( report=True )

    def getNumCtrls( self, hasMultiNodeRounds ):
        if hasMultiNodeRounds:
            try:
                main.cycle
            except Exception:
                main.cycle = 0
            main.cycle += 1
            # main.scale[ 0 ] determines the current number of ONOS controller
            main.numCtrls = int( main.scale.pop( 0 ) )
        else:
            main.numCtrls = main.maxNodes

    def killingAllOnos( self, killRemoveMax, stopOnos ):
        # kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                      " before initiating environment setup" )

        for i in range( main.maxNodes if killRemoveMax else main.numCtrls ):
            if stopOnos:
                main.ONOSbench.onosStop( main.ONOSip[ i ] )
            main.ONOSbench.onosKill( main.ONOSip[ i ] )

    def createApplyCell( self, newCell, cellName, Mininet, useSSH ):
        if newCell:
            tempOnosIp = []
            for i in range( main.numCtrls ):
                tempOnosIp.append( main.ONOSip[i] )

            main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                           cellName,
                                           Mininet if isinstance( Mininet, str ) else
                                           Mininet.ip_address,
                                           main.apps,
                                           tempOnosIp,
                                           main.ONOScli1.karafUser,
                                           useSSH=useSSH )
        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " +
                                       "environment",
                                 onfail="Failed to apply cell to environment " )
        return stepResult

    def uninstallOnos( self, killRemoveMax ):
        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for i in range( main.maxNodes if killRemoveMax else main.numCtrls ):
            onosUninstallResult = onosUninstallResult and \
                                  main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[ i ] )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosUninstallResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        return onosUninstallResult

    def buildOnos( self ):
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )
        return packageResult

    def installOnos( self, installMax ):
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE

        for i in range( main.ONOSbench.maxNodes if installMax else main.numCtrls ):
            options = "-f"
            if installMax and i >= main.numCtrls:
                options = "-nf"
            onosInstallResult = onosInstallResult and \
                                main.ONOSbench.onosInstall( node=main.ONOSip[ i ], options=options )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosInstallResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )
        if not onosInstallResult:
            main.cleanup()
            main.exit()
        return onosInstallResult

    def setupSsh( self ):
        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for i in range( main.numCtrls ):
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=main.ONOSip[ i ] )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )
        return secureSshResult

    def checkOnosService( self ):
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE
        main.step( "Starting ONOS service" )
        for i in range( main.numCtrls ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( main.ONOSip[ i ] )
            if onosIsUp == main.TRUE:
                main.log.report( "ONOS instance {0} is up and ready".format( i + 1 ) )
            else:
                main.log.report( "ONOS instance {0} may not be up, stop and ".format( i + 1 ) +
                                 "start ONOS again " )
                stopResult = stopResult and main.ONOSbench.onosStop( main.ONOSip[ i ] )
                startResult = startResult and main.ONOSbench.onosStart( main.ONOSip[ i ] )
                if not startResult or stopResult:
                    main.log.report( "ONOS instance {0} did not start correctly.".format( i + 1 ) )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready on all nodes",
                                 onfail="ONOS service did not start properly on all nodes" )
        return stepResult

    def startOnosClis( self ):
        startCliResult = main.TRUE
        main.step( "Starting ONOS CLI sessions" )
        pool = []
        main.threadID = 0
        for i in range( main.numCtrls ):
            t = main.Thread( target=main.CLIs[ i ].startOnosCli,
                            threadID=main.threadID,
                            name="startOnosCli-" + str( i ),
                            args=[ main.ONOSip[ i ] ] )
            pool.append( t )
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        if not startCliResult:
            main.log.info( "ONOS CLI did not start up properly" )
            main.cleanup()
            main.exit()
        else:
            main.log.info( "Successful CLI startup" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=startCliResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )
        return startCliResult

    def ONOSSetUp( self, Mininet, hasMultiNodeRounds=False, hasCli=True, newCell=True,
                   cellName="temp", removeLog=False, extraApply=None, arg=None, extraClean=None,
                   skipPack=False, installMax=False, useSSH=True, killRemoveMax=True,
                   CtrlsSet=True, stopOnos=False ):
        if CtrlsSet:
            self.getNumCtrls( hasMultiNodeRounds )

        main.case( "Starting up " + str( main.numCtrls ) +
                  " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( main.numCtrls ) + \
                               " node(s) ONOS cluster"
        self.killingAllOnos( killRemoveMax, stopOnos )

        main.log.info( "NODE COUNT = " + str( main.numCtrls ) )
        cellResult = True
        packageResult = True
        onosUninstallResult = True
        onosCliResult = True
        if not skipPack:
            cellResult = self.createApplyCell( newCell, cellName, Mininet, useSSH )

            if removeLog:
                main.log.info("Removing raft logs")
                main.ONOSbench.onosRemoveRaftLogs()

            onosUninstallResult = self.uninstallOnos( killRemoveMax )

            if extraApply is not None:
                extraApply( metadataMethod=arg ) if arg is not None else extraApply()

            packageResult = self.buildOnos()

        onosInstallResult = self.installOnos( installMax )

        if extraClean is not None:
            extraClean()
        secureSshResult = True
        if useSSH:
            secureSshResult = self.setupSsh()

        onosServiceResult = self.checkOnosService()

        if hasCli:
            onosCliResult = self.startOnosClis()

        return cellResult and packageResult and onosUninstallResult and \
               onosInstallResult and secureSshResult and onosServiceResult and onosCliResult
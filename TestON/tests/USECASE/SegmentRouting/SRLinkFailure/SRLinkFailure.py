"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
# In this test we perform a link failure and then test for connectivity
# CASE1: 2x2 topo + link failure + IP connectivity test
# CASE2: 4x4 topo + link failure + IP connectivity test
# CASE4: 2x2 topo + 3-node ONOS CLUSTER + link failure + IP connectivity test
# CASE5: 4x4 topo + 3-node ONOS CLUSTER + link failure + IP connectivity test


class SRLinkFailure:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )

        main.cfgName = '2x2'
        main.Cluster.setRunningNode( 1 )
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        # link failure
        run.killLink( main, 'spine101', 'leaf2', switches='4', links='6' )
        run.pingAll( main, "CASE1_Failure" )
        run.restoreLink( main, 'spine101', 'leaf2', 'of:0000000000000101',
                         'of:0000000000000002', '2', '3', '4', '8' )
        run.pingAll( main, "CASE1_Recovery" )
        # TODO Dynamic config of hosts in subnet
        # TODO Dynamic config of host not in subnet
        # TODO Dynamic config of vlan xconnect
        # TODO Vrouter integration
        # TODO Mcast integration
        run.cleanup( main )

    def CASE2( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.Cluster.setRunningNode( 1 )
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        # link failure
        run.killLink( main, 'spine101', 'leaf2', switches='8', links='30' )
        run.pingAll( main, "CASE2_Failure" )
        run.restoreLink( main, 'spine101', 'leaf2', 'of:0000000000000101',
                         'of:0000000000000002', '2', '3', '8', '32' )
        run.pingAll( main, "CASE2_Recovery" )
        # TODO Dynamic config of hosts in subnet
        # TODO Dynamic config of host not in subnet
        # TODO preconfigured xconnect
        # TODO Vrouter integration
        # TODO Mcast integration
        run.cleanup( main )

    def CASE4( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )
        main.cfgName = '2x2'
        main.Cluster.setRunningNode( 3 )
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        # link failure
        run.killLink( main, 'spine101', 'leaf2', switches='4', links='6' )
        run.pingAll( main, "CASE3_Failure" )
        run.restoreLink( main, 'spine101', 'leaf2', 'of:0000000000000101',
                         'of:0000000000000002', '2', '3', '4', '8' )
        run.pingAll( main, "CASE3_Recovery" )
        # TODO Dynamic config of hosts in subnet
        # TODO Dynamic config of host not in subnet
        # TODO Dynamic config of vlan xconnect
        # TODO Vrouter integration
        # TODO Mcast integration
        run.cleanup( main )

    def CASE5( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.Cluster.setRunningNode( 3 )
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        # link failure
        run.killLink( main, 'spine101', 'leaf2', switches='8', links='30' )
        run.pingAll( main, "CASE2_Failure" )
        run.restoreLink( main, 'spine101', 'leaf2', 'of:0000000000000101',
                         'of:0000000000000002', '2', '3', '8', '32' )
        run.pingAll( main, "CASE2_Recovery" )
        # TODO Dynamic config of hosts in subnet
        # TODO Dynamic config of host not in subnet
        # TODO preconfigured xconnect
        # TODO Vrouter integration
        # TODO Mcast integration
        run.cleanup( main )

'''Generates a DrawIO compatible XML file for network diagrams.
This module provides a class `NetPlot` that allows users to create network diagrams
'''

import xml.etree.ElementTree as ET
import logging

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NetPlot():
    '''
        Creates the DrawIO Plot XML file , based on Jgraph template
    '''
    def __init__(self):
        # initiating the blocks needed for the DrawIO XML template , standard in every plot
        self.mxfile = ET.Element('mxfile',host="app.diagrams.net",agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36", version="27.1.5")
        self.diagram = ET.SubElement(self.mxfile,'diagram',id="diagram_1",name="Page-1")
        self.mxGraphModel = ET.SubElement(self.diagram,
                                            'mxGraphModel',
                                            grid="1",
                                            gridSize="10",
                                            guides="1",
                                            tooltips="1",
                                            connect="1",
                                            arrows="1",
                                            fold="1",
                                            page="1",
                                            pageScale="1",
                                            pageWidth="850",
                                            pageHeight="1100",
                                            math="0",
                                            shadow="0")
        self.root = ET.SubElement(self.mxGraphModel,'root')
        self.mxCellID0 = ET.SubElement(self.root,'mxCell' , id="0")
        # Each Node and Edge are a child to the Parent id "1" 
        self.mxCellID1 = ET.SubElement(self.root,'mxCell' , id="1" , parent="0" , style=";html=1;") 

    def _getMXgraphShape(self,nodeType):
        # Defining the shape that can be used , it uses shapes already shipped with DrawIO application (More shapes will be added)
        # we are also using the "nodeLevel" variable to set the hirarichy of the plot if standards are not adhered by in using library
        if nodeType == 'Router':
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'50',
                    'height':'50',
                    'nodeLevel':'1'
                    }
        elif nodeType == 'Switch':
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=l2_switch;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'50',
                    'height':'50',
                    'nodeLevel':'3'}
        elif nodeType == 'l3_switch':
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=l3_switch;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'50',
                    'height':'50',
                    'nodeLevel':'2'}
        elif nodeType == 'firewall':
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=firewall;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'64',
                    'height':'50',
                    'nodeLevel':'2'}
        elif nodeType == 'server':
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=server;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'27',
                    'height':'50',
                    'nodeLevel':'4'}
        else :
            return {'style':'shape=mxgraph.cisco19.rect;prIcon=server;fillColor=#FAFAFA;strokeColor=#666666;html=1;',
                    'width':'27',
                    'height':'50',
                    'nodeLevel':'4'}


    def addNode(self,nodeName,nodeDescription='',nodeType=''):
        try:
            shapeParameters = self._getMXgraphShape(nodeType)
            mxCell = ET.SubElement(self.root,
                                    'mxCell', 
                                    id=nodeName,
                                    value=nodeName,
                                    style=("verticalLabelPosition=bottom;"
                                            "html=1;"
                                            "verticalAlign=top;"
                                            "aspect=fixed;align=center;"
                                            "pointerEvents=1;"
                                            f"{shapeParameters['style']}"
                                            ""),
                                    parent="1",
                                    vertex="1")
            mxGeometry = ET.SubElement(mxCell, 'mxGeometry',width=shapeParameters['width'] ,height=shapeParameters['height'] )
            mxGeometry.set('as','geometry')
            return
        except Exception as e:
            logging.error('Error in adding Node: {}'.format(e))

    def addNodeList(self,nodeListOfDictionary):
        try:
            for node in nodeListOfDictionary:
                self.addNode(nodeName=node['id'],nodeDescription=node['id'],nodeType=node['type'])
            return
        except Exception as e:
            logging.error('Error in adding Node List: {}'.format(e))

    def addLink(self,sourceNodeID,destinationNodeID,localPort,remotePort): 

        mxCell = ET.SubElement(self.root,
                                'mxCell',
                                id=sourceNodeID+localPort+destinationNodeID+remotePort,
                                style="endFill=0;endArrow=none;",
                                parent="1",
                                source=sourceNodeID,
                                target=destinationNodeID,
                                edge="1")
        mxGeometry = ET.SubElement(mxCell, 'mxGeometry')
        mxGeometry.set('as','geometry')
        ### adding the Linklabels
        mcCell = ET.SubElement(self.root,
                               'mxCell',
                               id=sourceNodeID+localPort+destinationNodeID+remotePort+'source',
                               value=localPort,
                               parent=sourceNodeID+localPort+destinationNodeID+remotePort,
                               style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];",
                               connectabe="0",
                               vertex="1")
        mcGeometry = ET.SubElement(mcCell, 'mxGeometry')
        mcGeometry.set('relative','1')
        mcGeometry.set('x','-0.85')
        mcGeometry.set('as','geometry')
        mxPoint = ET.SubElement(mcGeometry, 'mxPoint')
        mxPoint.set('as','offset')
        mcCell = ET.SubElement(self.root,
                               'mxCell',
                               id=sourceNodeID+localPort+destinationNodeID+remotePort+'dest',
                               value=remotePort,
                               parent=sourceNodeID+localPort+destinationNodeID+remotePort,
                               style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];",
                               connectabe="0",
                                vertex="1")
        mcGeometry = ET.SubElement(mcCell, 'mxGeometry')
        mcGeometry.set('relative','1')
        mcGeometry.set('x','0.85')      
        mcGeometry.set('as','geometry')

        
        mxPoint = ET.SubElement(mcGeometry, 'mxPoint')
        mxPoint.set('as','offset')


                                                                                        


    def addLinkList(self,linkListOfDictionary):
        try:
            for link in linkListOfDictionary:
                #print(link)
                self.addLink(sourceNodeID=link['from'] , destinationNodeID=link['to'], localPort=link['local_port'], remotePort=link['remote_port'])   
            logging.debug('Link List added successfully from ')

            return
        except Exception as e:
            logging.error('Error in adding Link List: {}'.format(e))

    def display_xml(self):
        logging.debug('Displaying XML content')
        return ET.tostring(self.mxfile) 

    def exportXML(self, filePath):
        with open(filePath,'wb') as file:
            tree = ET.ElementTree(self.mxfile)
            tree.write(file)
        return

    def __repr__(self):
        return str(self.display_xml())
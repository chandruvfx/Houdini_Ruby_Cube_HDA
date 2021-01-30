from PySide2 import QtCore
from PySide2 import QtWidgets

code='''
from collections import OrderedDict
import json
hou.playbar.setRealTime(True)
hou.playbar.setPlayMode(hou.playMode.Once)

def solve(node):
    """solve rubik to solved state"""
    objnode = hou.node("/obj/%s/Ruby" %node)
 
    if(len(objnode.glob('Trans*'))<1):
        pass
    else:
        all_trans = objnode.glob('Trans*')
        all_grp = objnode.glob('rotate*')
        all_sort = objnode.glob('sort*')
        
        for trans in all_trans:
            trans.destroy()
        for grp in all_grp:
            grp.destroy()
        for sort in all_sort:
            sort.destroy()
    # each time when i press rotation button in digital asset 
    # It create an plaback event handler for each rotation button
    # This event handle need to get delete if transform nodes get deleted    
    # otherwise it stays and provide errors
    # To check remove two print statement in enable which commeneted
    hou.playbar.clearEventCallbacks()
        
def rotation(node, grp_pattern,axis, num,angle):
    """ Rotation 
        node = Current node name example:subnet1
        grp_pattern = grop pattern combination list
        axis = which axis x or y or z
        angle = passed angle to set transform """
        
    if axis == 'X':
        mode = 1
    elif axis=='Y':
        mode = 2
    else:
        mode =3
        
    def create_nodes(rotsideaxis):
    
        grp =objnode.createNode('groupcreate')
        if num ==0:
            grp.setName('rotate_%s_plus' %axis,unique_name=True)
        else:
            grp.setName('rotate_middele%s_plus_90_%s' %(num,axis),unique_name=True)
        grp.parm('groupname').set("`opname(\'.\')`")
        grp.parm('basegroup').set(str(grp_pattern))
        grp.setInput(0,sort_x)
        
        trans = objnode.createNode('xform')
        trans.setName('Translate',unique_name=True)
        trans.parm("group").set(grp.name())
        #Set 0 in keyframe 1
        zerosetKey = hou.Keyframe()
        zerosetKey.setFrame(1)
        zerosetKey.setValue(0)
        
        #Set received angle in keyframe 20
        anglekey= hou.Keyframe()
        anglekey.setFrame(20)
        anglekey.setValue(int(angle))
        
        # once animation done from 0 to 20 we set angle revert to 90 
        #in first frame
        finalplayedkey= hou.Keyframe()
        finalplayedkey.setFrame(1)
        finalplayedkey.setValue(int(angle))
                
        if rotsideaxis == 1:
            # set rotation x to 0 in 1 and 90 in 20 th frames
            trans.parm("rx").setKeyframe(zerosetKey)
            trans.parm("rx").setKeyframe(anglekey)
            
            # play the rotation
            hou.playbar.play()
            
            #This event call back does followa once the rotation of 20 frames played
            # we reseting rotation x again 90 to 0 thframe 
            #reset our play back sildder to 1
            def outputPlaybarEvent(event_type, frame):
                if frame == 20:  
                    trans.parm("rx").setKeyframe(finalplayedkey)
                    trans.parm("rx").deleteAllKeyframes()
                    hou.setFrame(1)
            hou.playbar.addEventCallback(outputPlaybarEvent) 
                                                  
        elif rotsideaxis == 2:
            #similar like rotation axis x
            trans.parm("ry").setKeyframe(zerosetKey)
            trans.parm("ry").setKeyframe(anglekey)
            hou.playbar.play() 
            def outputPlaybarEvent(event_type, frame):
                if frame == 20:  
                    trans.parm("ry").setKeyframe(finalplayedkey)
                    trans.parm("ry").deleteAllKeyframes()
                    hou.setFrame(1)
            hou.playbar.addEventCallback(outputPlaybarEvent)
            
        else:
            #similar like rotation axis z
            trans.parm("rz").setKeyframe(zerosetKey)
            trans.parm("rz").setKeyframe(anglekey)
            hou.playbar.play() 
            def outputPlaybarEvent(event_type, frame):
                if frame == 20:  
                    trans.parm("rz").setKeyframe(finalplayedkey)
                    trans.parm("rz").deleteAllKeyframes()
                    hou.setFrame(1)
            hou.playbar.addEventCallback(outputPlaybarEvent)

        trans.setInput(0,grp)
        bevel = hou.node("/obj/%s/Ruby/polybevel1" %node)
        bevel.setInput(0,trans)
        bevel.setDisplayFlag(True)
        
    objnode = hou.node("/obj/%s/Ruby" %node)
    attr2 = hou.node("/obj/%s/Ruby/attribtransfer2" %node)   
    if(len(objnode.glob('Trans*'))<1):
        sort_x = objnode.createNode('sort')
        sort_x.parm("primsort").set(mode) 
        sort_x.setInput(0,attr2)
        create_nodes(mode)
        
    else:
        transnodes = objnode.glob('Trans*')
        for transnode in range(len(transnodes)):
            if transnode ==len(transnodes)-1:
                sort_x = objnode.createNode('sort')
                sort_x.parm("primsort").set(mode) 
                sort_x.setInput(0,transnodes[transnode])
                create_nodes(mode)  
    #print hou.playbar.eventCallbacks()
    objnode.layoutChildren()
    
def save_state(node):
    """Saving into json"""
    objnode = hou.node("/obj/%s/Ruby" %node)
    
    if(len(objnode.glob('Trans*'))<1):
        pass
    else:
        all_trans = objnode.glob('Trans*')
        all_grp = objnode.glob('rotate*')
        all_sort = objnode.glob('sort*')
        
        json_dict=OrderedDict()
        for trans,grp,sort in zip(all_trans,all_grp,all_sort):
            trans_name = trans.name()
            grp_name = grp.name()
            sort_name = sort.name()
            
            primsort = sort.parm("primsort").eval()
            grp_pattern = grp.parm('basegroup').rawValue()         
            value_tuple = trans.parmTuple('r').eval()
            
            json_dict[sort_name]=primsort
            json_dict[grp_name]=grp_pattern 
            json_dict[trans_name]=value_tuple
            
        json_object = json.dumps(json_dict, indent = 4) 
        with open(hou.hscriptExpression("$HIP")+"/"+"ruby.json", "w") as outfile: 
            outfile.write(json_object)
    hou.ui.displayMessage("Ruby state successfully saved in %s" %hou.hscriptExpression("$HIP"),\
         severity=hou.severityType.Message, title="success")  
            
def load_state(node):
    """ Load the saved json data"""
    solve(node)
    
    objnode = hou.node("/obj/%s/Ruby" %node)
    attr2 = hou.node("/obj/%s/Ruby/attribtransfer2" %node)   
    trans_nodes =[]     
    with open(hou.hscriptExpression("$HIP")+"/"+"ruby.json") as jsonfile:
        json_nodes = json.load(jsonfile, object_pairs_hook=OrderedDict)
    for k,v in json_nodes.items():
        if k == 'sort1':                 
            sort1 = objnode.createNode('sort')
            sort1.parm("primsort").set(v)
            sort1.setInput(0,attr2)
        elif k.startswith('sort') and k!='sort1':
            sort = objnode.createNode('sort')
            sort.parm("primsort").set(v)
            
        elif k.startswith('rotate'): 
            grp =objnode.createNode('groupcreate')
            grp.setName(k,unique_name=True)
            grp.parm('groupname').set("`opname('.')`")
            grp.parm('basegroup').set(str(v))
            try:
                grp.setInput(0,sort)
            except UnboundLocalError:  
                grp.setInput(0,sort1)
        elif k.startswith('Translate'):
            trans = objnode.createNode('xform')
            trans.setName(k,unique_name=True)
            trans.parm("group").set(grp.name())
            trans.parmTuple('r').set((tuple(v)))
            trans.setInput(0,grp)
            trans_nodes.append(trans)
        if k.startswith('sort') and k!='sort1':
            sort.setInput(0,trans)
            
    lengthtrans = len(trans_nodes)-1
    bevel = hou.node("/obj/%s/Ruby/polybevel1" %node)
    
    for trans in trans_nodes:
        if trans.name() ==  trans_nodes[lengthtrans].name():
            bevel.setInput(0,trans)
            bevel.setDisplayFlag(True)
    objnode.layoutChildren()
 
'''
class Ruby(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        
        self.initialize_ruby()
        
    def initialize_ruby(self):
            
        self.label = QtWidgets.QLabel('Enter Ruby Size',self)
        self.label.move(20,30)
    
        self.ruby_size = QtWidgets.QLineEdit(self)
        self.ruby_size.setText('3')
        self.ruby_size.move(140,30)
        
        self.createruby = QtWidgets.QPushButton('Create',self)
        self.createruby.move(110,90)
        self.createruby.clicked.connect(self.create_ruby)
        
        self.setGeometry(300, 200, 300, 200)
        self.setWindowTitle('Ruby Generator')
        
    def genral_first_grplogic(self):
        ''' Generate grouping logic 
            Example : If 5 is input  logic is
            5 X 5 X 6(ruby single piece size) = 150
            9(emptypoints)X6 = 54
            150-54=96'''            
        
        self.occur = []
        self.grp_logic=[]
        
        #Each piece in ruby has 6 face 
        ruby_faces = 6
        self.ruby_size_XYZ = int(self.ruby_size.text())*int(self.ruby_size.text())
        
        #MULTIPLY ROW ANFD CLOLUMN
        self.first_ruby_size =self.ruby_size_XYZ*ruby_faces
        self.occur.append(self.first_ruby_size)
        
        #subtract the already filled points or gap points expample:9 if 5 is size
        ruby_faces_pts = int(self.ruby_size.text())-2
        #row and column gap points multipled with ruby size 
        self.ruby_removed_faces_pts = (ruby_faces_pts * ruby_faces_pts)*ruby_faces
        #sub ruby size to gaap points to get the faces of primitives
        self.removed_occur=self.first_ruby_size - self.ruby_removed_faces_pts
        
        #append in list of three consicutive addition
        for i in range( int(self.ruby_size.text())-2):
            self.occur.append(self.occur[i]+self.removed_occur)
        #1st gp logic occurance 
        self.grp_logic.append('0-{0}'.format(self.first_ruby_size-1))
        #remaining occurance 
        for occur in self.occur:
            #For last occurance add 150
            if occur == self.occur[-1]:
                self.grp_logic.append('{0}-`{0}+{1}`'.format(occur,self.first_ruby_size))
            else:
                self.grp_logic.append('{0}-`{0}+{1}`'.format(occur,self.removed_occur-1))
        return self.grp_logic
                                       
        pass
        
    def create_ruby(self):
    
        ''' Creating ruby depending upon size of input '''
     
        # Create obj rby
        self.ruby_obj = hou.node("obj").createNode('geo')
        self.ruby_obj.setName('Ruby', unique_name=True)       
                                               
        # Create geo box and set axis division by user input
        ruby_geo = self.ruby_obj.createNode('box')
        ruby_geo.parm('type').set(1)
        ruby_geo.parmTuple('divrate').set((int(self.ruby_size.text()),\
                int(self.ruby_size.text()),int(self.ruby_size.text())))
        add_geo = self.ruby_obj.createNode('add')
        add_geo.setInput(0,ruby_geo)
        add_geo.parm('keep').set(1)
         
        #Create Attrib wrangle and set distance of points
        attr_wrangle = self.ruby_obj.createNode('attribwrangle')
        attr_wrangle.setInput(0,add_geo)
        dist='''vector p1 = point(0,"P",0);
        vector p2 = point(0,"P",1);
        v@dis = distance(p1,p2);'''
        attr_wrangle.parm('snippet').set(dist)
        
        instance_ruby_geo = self.ruby_obj.createNode('box')
              
        copystamp_size_trans = self.ruby_obj.createNode('xform')
        copystamp_size_trans.setName('xform')
        copystamp_size_trans.setInput(0,instance_ruby_geo)
        copystamp_size_trans.parmTuple('s').set((0.98,0.98,0.98))
        copystamp_size_trans.parm('scale').setExpression('stamp("../copy1","discube",0)')
        
        copystamp = self.ruby_obj.createNode('copy')
        copystamp.setInput(0,copystamp_size_trans)
        copystamp.setInput(1,attr_wrangle)
        copystamp.parm('stamp').set(1)
        copystamp.parm('param1').set('discube')
        copystamp.parm('val1').setExpression('@dis')
        copystamp.parm('doattr').set(1)
        
        boung_geo = self.ruby_obj.createNode('bound')
        boung_geo.setInput(0,copystamp)
        boung_geo.parmTuple('minsize').set((1.4,1.4,1.4))
        
        ruby_clr = {'Red':(1,0,0), 'Green':(0,1,0), 'Blue':(0,0,1),\
                    'Yellow':(1,1,0), 'Rose':(1,0,1), 'White': (1,1,1)}
        
        #each Face number access through this counter and labeled as group name
        c=0
        ruby_clr_nodes = []
        for k,v in ruby_clr.items():
            ruby_clr_node= self.ruby_obj.createNode('color')
            ruby_clr_node.setName(k)
            ruby_clr_node.parm('group').set(str(c))
            ruby_clr_node.parm('class').set(1)
            ruby_clr_node.parmTuple('color').set((v[0],v[1],v[2]))
            ruby_clr_nodes.append(ruby_clr_node)
            c=c+1
        
        ruby_clr_nodes[0].setInput(0,boung_geo)
        n=1
        while n<len(ruby_clr_nodes):
            ruby_clr_nodes[n].setInput(0,ruby_clr_nodes[n-1])
            n=n+1
            
        attr_trans = self.ruby_obj.createNode('attribtransfer')
        attr_trans.parm('thresholddist').set(0.79)
        attr_trans.setInput(1,ruby_clr_nodes[(len(ruby_clr_nodes))-1])
        attr_trans.setInput(0,copystamp)
        
        main_clr = self.ruby_obj.createNode('color')
        main_clr.setInput(0,ruby_geo)
        main_clr.parm('class').set(1)
        main_clr.parmTuple('color').set((0,0,0))
        
        attr_trans_black = self.ruby_obj.createNode('attribtransfer')
        attr_trans_black.parm('thresholddist').set(0.12)
        attr_trans_black.setInput(1,main_clr)
        attr_trans_black.setInput(0,attr_trans)
        
        polyext = self.ruby_obj.createNode('polybevel')
        polyext.parm('offset').set(.02)
        polyext.parm('divisions').set(2)
        polyext.setInput(0,attr_trans_black)
        polyext.setDisplayFlag(True)
        
        hou.node("obj/%s" %(self.ruby_obj)).layoutChildren()
        
        #Create subnet
        nodeTup = ()
        self.subnetNode = hou.node("/obj").createNode("subnet")
        self.subnetNode.setName('RubyGEN')
        nodeTup = nodeTup + (self.ruby_obj,)
        hou.moveNodesTo(nodeTup, self.subnetNode)
        
        #made a digital asset
        hda_node = self.subnetNode.createDigitalAsset(
            name='Ruby',
            hda_file_name=hou.hscriptExpression("$HIP")+'/'+'ruby.hda')
        #Enable the python modeule and insert the code into the HDA script tab
        asset_definition = hda_node.type().definition()
        section = asset_definition.addSection('PythonModule')
        asset_definition.setExtraFileOption('PythonModule/IsPython', True)       
        section.setContents(code)      
        
        #Create an spare param folder for ruby controls
        parm_group = hda_node.parmTemplateGroup()        
        ruby_folder = hou.FolderParmTemplate('ruby', 'Ruby Ctrls')
        
        #Add all the controllers
        ruby_folder.addParmTemplate(hou.SeparatorParmTemplate('sep'))
        for axis in ['X','Y','Z']:
            ruby_folder.addParmTemplate(hou.LabelParmTemplate('%s' %axis,'%s' %axis))
            for ruby_ctrls in range(int(self.ruby_size.text())):
                if ruby_ctrls == 0 :
                    if axis =='X':
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('right_%s' %axis,'Right',join_with_next=True))
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_right_p90', 'Rotate +90',\
                            #when button clickes we call the call back script
                            #by passing subnet name, grp pattern list, which axis, number, angle 
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_right_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
                    elif axis =='Z':
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('front_%s' %axis,'Front',join_with_next=True))
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_front_p90', 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_front_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
                    else:
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('lower_%s' %axis,'Lower',join_with_next=True))
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_lower_p90', 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_lower_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[0],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
                elif ruby_ctrls>=1 and ruby_ctrls<=int(self.ruby_size.text())-2:
                    ruby_folder.addParmTemplate(hou.LabelParmTemplate('middle_%s_%d' %(axis,ruby_ctrls),'Middle_%d' %ruby_ctrls, join_with_next=True ))     
                    ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_middle_p90%s_%s' %(axis,ruby_ctrls), 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '%s', '90')" %(self.genral_first_grplogic()[ruby_ctrls],axis,ruby_ctrls), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                    ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_middle_n90%s_%s' %(axis,ruby_ctrls), 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '%s', '-90')" %(self.genral_first_grplogic()[ruby_ctrls],axis,ruby_ctrls), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                            
                elif ruby_ctrls== int(self.ruby_size.text())-1:
                    if axis =='X':
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('left_%s' %axis,'Left',join_with_next=True))
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_left_p90', 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_left_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
                    elif axis =='Z':
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('back_%s' %axis,'Back',join_with_next=True))  
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_back_p90', 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_back_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
                    else:
                        ruby_folder.addParmTemplate(hou.LabelParmTemplate('upper_%s' %axis,'Upper',join_with_next=True))
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_upper_p90', 'Rotate +90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            join_with_next=True))
                            
                        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('rot_upper_n90', 'Rotate -90',\
                            script_callback="kwargs['node'].hdaModule().rotation(kwargs['node'], '%s', '%s', '0', '-90')" %(self.genral_first_grplogic()[ruby_ctrls],axis), script_callback_language=hou.scriptLanguage.Python,\
                            ))
                        
            ruby_folder.addParmTemplate(hou.SeparatorParmTemplate('sep_%s' %axis))
        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('solve', 'Solve', script_callback="kwargs['node'].hdaModule().solve(kwargs['node'])", script_callback_language=hou.scriptLanguage.Python))
        ruby_folder.addParmTemplate(hou.SeparatorParmTemplate('sep_1'))
        
        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('save', 'Save State', script_callback="kwargs['node'].hdaModule().save_state(kwargs['node'])", script_callback_language=hou.scriptLanguage.Python))
        ruby_folder.addParmTemplate(hou.ButtonParmTemplate('load', 'Load State', script_callback="kwargs['node'].hdaModule().load_state(kwargs['node'])", script_callback_language=hou.scriptLanguage.Python))
        parm_group.append(ruby_folder)  
        hda_node.setParmTemplateGroup(parm_group)
        
        #get ruby folder delete it and move to transform tab 
        ruby_fol = parm_group.findFolder("Ruby Ctrls")
        parm_group.remove(ruby_fol)
        trans = parm_group.findFolder("Transform")
        parm_group.insertBefore(trans,ruby_folder)
        hda_node.setParmTemplateGroup(parm_group)
        
        hou.playbar.clearEventCallbacks()
        hou.playbar.setFrameRange(1,20)
        hou.setFrame(1)
        self.close()
        pass
        
dialog = Ruby()
dialog.show()

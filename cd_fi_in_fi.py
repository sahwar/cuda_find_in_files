﻿''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github.com)
Version:
    '2.2.01 2017-06-28'
ToDo: (see end of file)
'''

import  re, os, sys, locale, json, collections, copy

import  cudatext            as app
from    cudatext        import ed
import  cudax_lib           as apx
MIN_API_VER = '1.0.178'
MIN_API_VER = '1.0.180' # panel group p
MIN_API_VER = '1.0.183' # on_change

from    .cd_plug_lib        import *
from    .cd_fif_api         import *

odict = collections.OrderedDict

pass;                          #Tr.tr   = Tr(apx.get_opt('fif_log_file', '')) if apx.get_opt('fif_log_file', '') else Tr.tr
pass;                           LOG     = (-1== 1)         or apx.get_opt('fif_LOG'   , False) # Do or dont logging.
pass;                           from pprint import pformat
pass;                           pf=lambda d:pformat(d,width=150)
pass;                           ##!! waits correction

_   = get_translation(__file__) # I18N

VERSION     = re.split('Version:', __doc__)[1].split("'")[1]
VERSION_V,  \
VERSION_D   = VERSION.split(' ')

MAX_HIST= apx.get_opt('ui_max_history_edits', 20)
CFG_JSON= CdSw.get_setting_dir()+os.sep+'cuda_find_in_files.json'
#CFG_JSON= app.app_path(app.APP_DIR_SETTINGS)+os.sep+'cuda_find_in_files.json'

CLOSE_AFTER_GOOD= apx.get_opt('fif_hide_if_success'         , False)
USE_EDFIND_OPS  = apx.get_opt('fif_use_edfind_opt_on_start' , False)
DEF_LOC_ENCO    = 'cp1252' if sys.platform=='linux' else locale.getpreferredencoding()
loc_enco        = apx.get_opt('fif_locale_encoding', DEF_LOC_ENCO)
#if 'sw'==app.__name__:
#   USE_EDFIND_OPS  = False

#GAP     = 5

totb_l          = [TOTB_NEW_TAB, TOTB_USED_TAB]
shtp_l          = [SHTP_SHORT_R, SHTP_SHORT_RCL
                  ,SHTP_MIDDL_R, SHTP_MIDDL_RCL
                  ,SHTP_SPARS_R, SHTP_SPARS_RCL
                  ,SHTP_SHRTS_R, SHTP_SHRTS_RCL
                  ]
dept_l          = [_('All'), _('In folder only'), _('1 level'), _('2 levels'), _('3 levels'), _('4 levels'), _('5 levels')]
skip_l          = [_("Don't skip"), _('Hidden'), _('Binary'), _('Hidden, Binary')]
sort_l          = [_("Don't sort"), _('By date, from newest'), _('By date, from oldest')]
enco_l          = ['{}, UTF-8, '+ENCO_DETD 
                  ,'UTF-8, {}, '+ENCO_DETD 
                  ,'{}, '       +ENCO_DETD 
                  ,'UTF-8, '    +ENCO_DETD 
                  ,'{}, UTF-8'             
                  ,'UTF-8, {}'             
                  ,'{}'                    
                  ,'UTF-8'                 
                  ,              ENCO_DETD
                  ]     \
                    if loc_enco!='UTF-8' else   \
                  ['{}, '       +ENCO_DETD 
                  ,'{}'                    
                  ,              ENCO_DETD
                  ]
enco_l          = [f(enco, loc_enco) for enco in enco_l]

TOTB_L          = totb_l
SHTP_L          = shtp_l
DEPT_L          = dept_l
SKIP_L          = skip_l
SORT_L          = sort_l
ENCO_L          = enco_l

def reload_opts():
    api_reload_opts()
    
    global CLOSE_AFTER_GOOD,USE_EDFIND_OPS, loc_enco, enco_l
    CLOSE_AFTER_GOOD= apx.get_opt('fif_hide_if_success'         , False)
    USE_EDFIND_OPS  = apx.get_opt('fif_use_edfind_opt_on_start' , False)
    loc_enco        = apx.get_opt('fif_locale_encoding', DEF_LOC_ENCO)
    enco_l          = ['{}, UTF-8, '+ENCO_DETD 
                      ,'UTF-8, {}, '+ENCO_DETD 
                      ,'{}, '       +ENCO_DETD 
                      ,'UTF-8, '    +ENCO_DETD 
                      ,'{}, UTF-8'             
                      ,'UTF-8, {}'             
                      ,'{}'                    
                      ,'UTF-8'                 
                      ,              ENCO_DETD
                      ]     \
                        if loc_enco!='UTF-8' else   \
                      ['{}, '       +ENCO_DETD 
                      ,'{}'                    
                      ,              ENCO_DETD
                      ]
    enco_l          = [f(enco, loc_enco) for enco in enco_l]
   #def reload_opts()

def desc_fif_val(fifkey, val=None):
    pass;                      #LOG and log('fifkey, val={}',(fifkey, val))
    if val is None: return ''
    if False:pass
    elif fifkey in ('incl','excl','fold','frst'):   return val
    elif fifkey in ('reex','case','word'
                   ,'join','algn','cntx'):          return _('On') if val=='1' else _('Off')
    elif fifkey=='totb':    return totb_l[int(val)] if val in ('0', '1') else val
    val = int(val)
    if False:pass
    elif fifkey=='dept':    return dept_l[val] if 0<=val<len(dept_l) else ''
    elif fifkey=='skip':    return skip_l[val] if 0<=val<len(skip_l) else ''
    elif fifkey=='sort':    return sort_l[val] if 0<=val<len(sort_l) else ''
    elif fifkey=='enco':    return enco_l[val] if 0<=val<len(enco_l) else ''
    elif fifkey=='shtp':    return shtp_l[val] if 0<=val<len(shtp_l) else ''
   #def desc_fif_val


class Command:
#   def undo_by_report(self):
#       undo_by_report()
       #def undo_by_report

    def find_in_ed(self):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        filename= ed.get_filename()
        return dlg_fif(what='', opts=dict(
             incl = os.path.basename(filename) if filename else ed.get_prop(app.PROP_TAB_TITLE)
            ,fold = IN_OPEN_FILES
            ))
       #def find_in_ed

    def find_in_tabs(self):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        return dlg_fif(what='', opts=dict(
             incl = '*'
            ,fold = IN_OPEN_FILES
            ))
       #def find_in_ed

    def repeat_find_by_rpt(self):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        if ed.get_prop(app.PROP_LEXER_FILE).upper() not in lexers_l:
            return app.msg_status(_('The command works only with reports of FindInFile plugin'))
        req_opts  = report_extract_request(ed)
        if not req_opts:
            return app.msg_status(_('No info to Repeat Finding'))
        req_opts= json.loads(req_opts)
        what    = req_opts.pop('what', '')
        return dlg_fif(what=what, opts=req_opts)
       #def repeat_find_by_rpt

    def show_dlg(self, what='', opts={}):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        return dlg_fif(what, opts)

    def _nav_to_src(self, where:str, how_act='move'):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        return nav_to_src(where, how_act)
    def _jump_to(self, drct:str, what:str):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        return jump_to(drct, what)
    def on_goto_def(self, ed_self):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update application'))
        if ed_self.get_prop(app.PROP_LEXER_FILE).upper() in lexers_l:
            self._nav_to_src('same', 'move')
            return True
    def on_click_dbl(self, ed_self, scam):
        dcls    = Command.get_dcls()
        dcl     = dcls.get(scam, '')
        pass;                   LOG and log('scam, dcl={}',(scam, dcl))
        if not dcl:
            return
        if ed_self.get_prop(app.PROP_LEXER_FILE).upper() not in lexers_l:
            return
        return not self._nav_to_src(*dcl.split(','))
       #def on_click_dbl
    
    dcls    = None
    dcls_def= {'':'same,stay'}
    @staticmethod
    def get_dcls():
        if Command.dcls is None:
            stores  = json.loads(open(CFG_JSON).read(), object_pairs_hook=odict) \
                        if os.path.exists(CFG_JSON) and os.path.getsize(CFG_JSON) != 0 else \
                      odict()
            Command.dcls    = stores.get('dcls', Command.dcls_def)
        return Command.dcls
       #def get_dcls
    
    def dlg_nav_by_dclick(self):
        pass;                   LOG and log('ok',())
        dcls    = Command.get_dcls()
        godef   = apx.get_opt('mouse_goto_definition', 'a')
        hint    = _('See "mouse_goto_definition" in default.json and user.json')
        acts_l  = ["<no action>"
                  ,'Navigate to same group'
                  ,'Navigate to next group'
                  ,'Navigate to prev group'
                  ,'Navigate to next group, activate'
                  ,'Navigate to prev group, activate'
                  ]
        sgns_l  = [''
                  ,'same,stay'
                  ,'next,stay'
                  ,'prev,stay'
                  ,'next,move'
                  ,'prev,move'
                  ]
        aid,vals,*_t   = dlg_wrapper(_('Configure found result navigation by double-click'), 505,280,     #NOTE: dlg-dclick
             [dict(           tp='lb'    ,tid='nnn' ,l=5        ,w=220  ,cap=              '>[double-click]:'                               ) #
             ,dict(cid='nnn' ,tp='cb-ro' ,t=5       ,l=5+220+5  ,w=270  ,items=acts_l                                                       ) #
             ,dict(           tp='lb'    ,tid='snn' ,l=5        ,w=220  ,cap=        '>Shift+[double-click]:'                               ) #
             ,dict(cid='snn' ,tp='cb-ro' ,t=5+ 30   ,l=5+220+5  ,w=270  ,items=acts_l                                                       ) #
             ,dict(           tp='lb'    ,tid='ncn' ,l=5        ,w=220  ,cap=         '>Ctrl+[double-click]:'                               ) #
             ,dict(cid='ncn' ,tp='cb-ro' ,t=5+ 60   ,l=5+220+5  ,w=270  ,items=acts_l                                                       ) #
             ,dict(           tp='lb'    ,tid='scn' ,l=5        ,w=220  ,cap=   '>Shift+Ctrl+[double-click]:'                               ) #
             ,dict(cid='scn' ,tp='cb-ro' ,t=5+ 90   ,l=5+220+5  ,w=270  ,items=acts_l                                                       ) #
             ,dict(           tp='lb'    ,tid='nna' ,l=5        ,w=220  ,cap=          '>Alt+[double-click]:'   ,en=godef!='a'  ,hint=hint  ) #
             ,dict(cid='nna' ,tp='cb-ro' ,t=5+120   ,l=5+220+5  ,w=270  ,items=acts_l                           ,en=godef!='a'  ,hint=hint  ) #
             ,dict(           tp='lb'    ,tid='sna' ,l=5        ,w=220  ,cap=    '>Shift+Alt+[double-click]:'   ,en=godef!='sa' ,hint=hint  ) #
             ,dict(cid='sna' ,tp='cb-ro' ,t=5+150   ,l=5+220+5  ,w=270  ,items=acts_l                           ,en=godef!='sa' ,hint=hint  ) #
             ,dict(           tp='lb'    ,tid='nca' ,l=5        ,w=220  ,cap=     '>Alt+Ctrl+[double-click]:'   ,en=godef!='ca' ,hint=hint  ) #
             ,dict(cid='nca' ,tp='cb-ro' ,t=5+180   ,l=5+220+5  ,w=270  ,items=acts_l                           ,en=godef!='ca' ,hint=hint  ) #
             ,dict(           tp='lb'    ,tid='sca' ,l=5        ,w=220  ,cap='>Shift+Ctrl+Alt+[double-click]:'  ,en=godef!='sca',hint=hint  ) #
             ,dict(cid='sca' ,tp='cb-ro' ,t=5+210   ,l=5+220+5  ,w=270  ,items=acts_l                           ,en=godef!='sca',hint=hint  ) #
             ,dict(cid='!'   ,tp='bt'    ,t=5+240   ,l=5+330    ,w=80   ,cap=_('OK')                            ,def_bt=True                ) #
             ,dict(cid='-'   ,tp='bt'    ,t=5+240   ,l=5+415    ,w=80   ,cap=_('Cancel')                                                    )              
             ],    dict(nnn=sgns_l.index(dcls.get('',   ''))
                       ,snn=sgns_l.index(dcls.get('s',  ''))
                       ,ncn=sgns_l.index(dcls.get('c',  ''))
                       ,scn=sgns_l.index(dcls.get('sc', ''))
                       ,nna=sgns_l.index(dcls.get('a',  ''))
                       ,sna=sgns_l.index(dcls.get('sa', ''))
                       ,nca=sgns_l.index(dcls.get('ca', ''))
                       ,sca=sgns_l.index(dcls.get('sca',''))
                       ), focus_cid='nnn')
        pass;              #LOG and log('vals={}',vals)
        if aid is None or aid=='-': return
        for nnn in ('nnn', 'snn', 'ncn', 'scn', 'nna', 'sna', 'nca', 'sca'):
            sca = nnn.replace('n', '')
            if 0==vals[nnn]:
                dcls.pop(sca, None)
            else:
                dcls[sca]   = sgns_l[vals[nnn]]
        Command.dcls    = dcls
        stores  = json.loads(open(CFG_JSON).read(), object_pairs_hook=odict) \
                    if os.path.exists(CFG_JSON) and os.path.getsize(CFG_JSON) != 0 else \
                  odict()
        stores['dcls']  = dcls
        open(CFG_JSON, 'w').write(json.dumps(stores, indent=4))
       #def dlg_nav_by_dclick

    def dlg_fif_opts(self):
        return dlg_fif_opts()
   #class Command

def dlg_fif_opts():
    try:
        from cuda_options_editor import dlg_opt_editor
    except:
        app.msg_status(_('To view/edit options install plugin cuda_options_editor'))
        return
    FIF_OPTS    = os.path.dirname(__file__)+os.sep+'fif_options.json'
    fif_opts    = json.loads(open(FIF_OPTS).read())
    dlg_opt_editor('FiF options', fif_opts, subset='fif.')
    reload_opts()
   #def dlg_fif_opts

def dlg_press(stores_main, hist_order, invl_l, desc_l):
    stores  = copy.deepcopy(stores_main)
    pset_l  = stores.setdefault('pset', [])
    stores.setdefault('pset_nnus', 0)
    keys_l  = ['reex','case','word'
              ,'incl','excl'
              ,'fold','dept'
              ,'skip','sort','frst','enco'
                     ,'totb','join','shtp','algn','cntx']
    invl_l  = invl_l[:]#   invl_l  = [v for v in invl_l]
    ouvl_l  = [v for v in invl_l]
    caps_l  = ['.*','aA','"w"'
              ,'In files','Not in files'
              ,'In folder','Subfolders'
              ,'Skip files','Sort file list','Firsts','Encodings'
              ,'Show in','Append results','Tree type','Align','Show context']
    def upgrd(ps:list)->list:
        if '_aa_' not in ps:  
            for k in ps:
                if k[0]=='_' and ps[k]=='_':
                    ps[k]   = '-'
            return ps
        _aa  = ps.pop('_aa_', '')
        _if  = ps.pop('_if_', '')
        _fo  = ps.pop('_fo_', '')
        _fn  = ps.pop('_fn_', '')
        _rp  = ps.pop('_rp_', '')
        ps['_reex'] = 'x' if _aa else '-'
        ps['_case'] = 'x' if _aa else '-'
        ps['_word'] = 'x' if _aa else '-'
        ps['_incl'] = 'x' if _if else '-'
        ps['_excl'] = 'x' if _if else '-'
        ps['_fold'] = 'x' if _if else '-'
        ps['_dept'] = 'x' if _if else '-'
        ps['_skip'] = 'x' if _fn else '-'
        ps['_sort'] = 'x' if _fn else '-'
        ps['_frst'] = 'x' if _fn else '-'
        ps['_enco'] = 'x' if _fn else '-'
        ps['_totb'] = 'x' if _rp else '-'
        ps['_join'] = 'x' if _rp else '-'
        ps['_shtp'] = 'x' if _rp else '-'
        ps['_algn'] = 'x' if _rp else '-'
        ps['_cntx'] = 'x' if _rp else '-'
        return ps
       #def upgrd
    for ps in pset_l:
        upgrd(ps)
    if hist_order:
        pset_l  = sorted(pset_l, key=lambda ps: ps.get('nnus', 0), reverse=True)

    dlg_list= [f(_('Restore: {}\t[{}{}{}].*aAw, [{}{}]In files, [{}{}]In folders, [{}{}{}{}]Adv. search, [{}{}{}{}{}]Adv. report')
                ,ps['name']
                ,ps['_reex'],ps['_case'],ps['_word']
                ,ps['_incl'],ps['_excl']
                ,ps['_fold'],ps['_dept']
                ,ps['_skip'],ps['_sort'],ps['_frst'],ps['_enco']
                ,ps['_totb'],ps['_join'],ps['_shtp'],ps['_algn'],ps['_cntx']
                ) 
                for ps in pset_l] \
            + [f(_('In folder={}\tFind in all opened documents'), IN_OPEN_FILES)
              ,_('Config presets…\tChange, Move up/down, Delete')
              ,_('Save as preset\tSelect options to save…')]
    ind_inop= len(pset_l)
    ind_conf= len(pset_l)+1
    ind_save= len(pset_l)+2
    ps_ind  = CdSw.dlg_menu(CdSw.MENU_LIST_ALT, '\n'.join(dlg_list))      #NOTE: dlg-menu-press
    pass;                      #LOG and log('ps_ind={}',(ps_ind))
    if ps_ind is None:  return None
    if False:pass
    elif ps_ind==ind_inop:
        # To find in open files
        ouvl_l[keys_l.index('fold')]    = IN_OPEN_FILES
        return ouvl_l
        
    elif ps_ind<len(pset_l):
        # Restore
        ps      = pset_l[ps_ind]
        stores['pset_nnus'] += 1
        ps['nnus'] = stores['pset_nnus']
        stores_main.update(stores)
        open(CFG_JSON, 'w').write(json.dumps(stores_main, indent=4))
        for i, k in enumerate(keys_l):
            if ps.get('_'+k, '')=='x':
                ouvl_l[i]   = ps.get(k, ouvl_l[i])
        app.msg_status(_('Options is restored from preset: ')+ps['name'])
        return ouvl_l
        
    elif ps_ind==ind_conf:
        # Config
        if not pset_l:  return app.msg_status(_('No preset to config'))

        def save_close(cid, ag):
            if pset_l:
                ps_ind      = ag.cval('prss')
                ps          = pset_l[ps_ind]
                ps['name']  = ag.cval('name')
            stores_main.update(stores)
            open(CFG_JSON, 'w').write(json.dumps(stores_main, indent=4))
            return None
            
        def acts(cid, ag):
            if not pset_l:  return {}
            ps_ind      = ag.cval('prss')
            ps          = pset_l[ps_ind]
            new_name    = ag.cval('name')
            prss_nms    = []
            if ps['name'] != new_name:
                ps['name']  = new_name
            if False:pass
            elif cid=='mvup' and ps_ind>0 \
            or   cid=='mvdn' and ps_ind<len(pset_l)-1:
                mv_ind  = ps_ind + (-1 if cid=='mvup' else 1)
                pset_l[mv_ind], \
                pset_l[ps_ind]  = pset_l[ps_ind], \
                                  pset_l[mv_ind]
                ps_ind  = mv_ind
                ps_mns  = [ps['name'] for ps in pset_l]
                return dict(
                    ctrls=[('prss',dict(items=ps_mns, val=ps_ind)   )
                          ,('mvup',dict(en=ps_ind>0)                )
                          ,('mvdn',dict(en=ps_ind<(len(pset_l)-1))  )
                          ]
                   ,fid='prss')
            elif cid=='delt':
                pset_l.pop(ps_ind)
                ps_ind  = min(ps_ind, len(pset_l)-1)
                ps      = pset_l[ps_ind]                                                                        if pset_l else {}
                pass;              #LOG and log('ps={}',(ps))
                ps_mns  = [ps['name'] for ps in pset_l]
                ps_its  = [f('{} -- {}', caps_l[i], desc_fif_val(k, ps.get(k))) for i, k in enumerate(keys_l)]  if pset_l else [' ']
                ps_vls  = [('1' if ps['_'+k]=='x' else '0')                     for    k in           keys_l ]  if pset_l else ['0']
                return dict(
                    ctrls=[('prss',dict(items=ps_mns, val=ps_ind)                   )
                          ,('name',dict(              val=ps['name'])               )
                          ,('what',dict(items=ps_its, val=(-1,ps_vls))              )
                          ,('mvup',dict(en=len(pset_l)>0 and ps_ind>0)              )
                          ,('mvdn',dict(en=len(pset_l)>0 and ps_ind<(len(pset_l)-1)))
                          ,('clon',dict(en=len(pset_l)>0)                           )
                          ,('delt',dict(en=len(pset_l)>0)                           )
                          ]
                   ,fid='prss')
            elif cid=='clon':
                ps  = pset_l[ps_ind]
                psd = {k:v for k,v in ps.items()}
                pset_l.insert(ps_ind, psd)
                ps_mns  = [ps['name'] for ps in pset_l]
                return dict(
                    ctrls=[('prss',dict(items=ps_mns, val=ps_ind)   )
                          ,('mvup',dict(en=ps_ind>0)                )
                          ,('mvdn',dict(en=ps_ind<(len(pset_l)-1))  )
                          ]
                   ,fid='prss')
            
            pass;               LOG and log('no act: cid,ps_ind={}',(cid,ps_ind))
            return {'fid':'prss'}
        
        def fill_what(cid, ag):
            ps_ind  = ag.cval('prss')
            prss_nms= [('prss',dict(val=ps_ind))]
            if pset_l:
                ps_ind_p    = ag.cval('prss', live=False)
                pass;          #LOG and log('ps_ind,ps_ind_p={}',(ps_ind,ps_ind_p))
                ps_p        = pset_l[ps_ind_p]
                if ps_p['name']!= ag.cval('name'):
                    ps_p['name']= ag.cval('name')
                    ps_mns      = [ps['name'] for ps in pset_l]
                    prss_nms    = [('prss',dict(items=ps_mns, val=ps_ind))]
            pass;              #LOG and log('ps_ind={}',(ps_ind))
            ps      = pset_l[ps_ind]                                                                        if pset_l else {}
            pass;              #LOG and log('ps={}',(ps))
            ps_its  = [f('{} -- {}', caps_l[i], desc_fif_val(k, ps.get(k))) for i, k in enumerate(keys_l)]  if pset_l else [' ']
            ps_vls  = [('1' if ps['_'+k]=='x' else '0')                     for    k in           keys_l ]  if pset_l else ['0']
            return dict(
                ctrls=[('what',dict(items=ps_its, val=(-1,ps_vls))  )
                      ,('name',dict(              val=ps['name'])   )
                      ,('mvup',dict(en=ps_ind>0)                    )
                      ,('mvdn',dict(en=ps_ind<(len(pset_l)-1))      )
                      ]+prss_nms
               ,fid='prss')

        ps_ind      = 0
        ps          = pset_l[ps_ind]                                                                        if pset_l else {}
        DLG_W       = 5*4+245+300
        ps_mns      = [ps['name'] for ps in pset_l]                                                         if pset_l else [' ']
        ps_its      = [f('{} -- {}', caps_l[i], desc_fif_val(k, ps.get(k))) for i, k in enumerate(keys_l)]  if pset_l else [' ']
        ps_vls      = [('1' if ps['_'+k]=='x' else '0')                     for    k in           keys_l ]  if pset_l else ['0']
        pass;              #LOG and log('ps_mns={}',(ps_mns))
        pass;              #LOG and log('ps_its={}',(ps_its))
        ctrls   = \
                 [('lprs',dict(tp='lb'      ,t=5            ,l=5        ,w=245  ,cap=_('&Presets:')                      )) # &p
                 ,('prss',dict(tp='lbx'     ,t=5+20,h=345   ,l=5        ,w=245  ,items=ps_mns       ,en=(len(pset_l)>0)  ,val=ps_ind    ,call=fill_what )) #
                  # Content
                 ,('lnam',dict(tp='lb'      ,t=5+20+345+10  ,l=5        ,w=245  ,cap=_('&Name:')                                                        )) # &n
                 ,('name',dict(tp='ed'      ,t=5+20+345+30  ,l=5        ,w=245                      ,en=(len(pset_l)>0)  ,val=ps.get('name', '')        )) # 
                  # Acts
                 ,('mvup',dict(tp='bt'      ,t=435          ,l=5        ,w=120  ,cap=_('Move &up')  ,en=(len(pset_l)>1) and ps_ind>0    ,call=acts      )) # &u
                 ,('mvdn',dict(tp='bt'      ,t=460          ,l=5        ,w=120  ,cap=_('Move &down'),en=(len(pset_l)>1)                 ,call=acts      )) # &d
                 ,('clon',dict(tp='bt'      ,t=435          ,l=5*2+120  ,w=120  ,cap=_('Clon&e')    ,en=(len(pset_l)>0)                 ,call=acts      )) # &e
                 ,('delt',dict(tp='bt'      ,t=460          ,l=5*2+120  ,w=120  ,cap=_('Dele&te')   ,en=(len(pset_l)>0)                 ,call=acts      )) # &t
                  #
                 ,('lwha',dict(tp='lb'      ,t=5            ,l=260      ,w=300  ,cap=_('&What to restore:')                                             )) # &w
                 ,('what',dict(tp='ch-lbx'  ,t=5+20,h=400   ,l=260      ,w=300  ,items=ps_its       ,en=F               ,val=(-1,ps_vls)                ))
                  #
                 ,('!'   ,dict(tp='bt'      ,t=435          ,l=DLG_W-5-100,w=100,cap=_('OK')        ,def_bt=True                        ,call=save_close)) # &
                 ,('-'   ,dict(tp='bt'      ,t=460          ,l=DLG_W-5-100,w=100,cap=_('Cancel')                                        ,call=LMBD_HIDE ))
                 ]
        DlgAgent(form   =dict(cap=_('Config presets'), w=DLG_W, h=490)
                ,ctrls  =ctrls
                ,fid    ='prss'
        ).show()
        return None
        
    elif ps_ind==ind_save:
        # Save
        pass;                  #LOG and log('ps_ind={}',(ps_ind))
        items   = [f('{} -- {}', caps_l[i], desc_l[i]) for i, k in enumerate(keys_l)]
        btn,vals,*_t   = dlg_wrapper(_('Save preset'), GAP+300+GAP,GAP+500+GAP,     #NOTE: dlg-pres-new
             [dict(           tp='lb'    ,t=GAP             ,l=GAP          ,w=300  ,cap=_('&Name:')            ) # &n
             ,dict(cid='name',tp='ed'    ,t=GAP+20          ,l=GAP          ,w=300                              ) # 
             ,dict(           tp='lb'    ,t=GAP+55          ,l=GAP          ,w=300  ,cap=_('&What to save:')    ) # &w
             ,dict(cid='what',tp='ch-lbx',t=GAP+75,h=390    ,l=GAP          ,w=300  ,items=items                )
             ,dict(cid='!'   ,tp='bt'    ,t=GAP+500-28      ,l=GAP+300-170  ,w=80   ,cap=_('OK')    ,def_bt=True) # &
             ,dict(cid='-'   ,tp='bt'    ,t=GAP+500-28      ,l=GAP+300-80   ,w=80   ,cap=_('Cancel')            )
             ],    dict(name=f(_('#{}: {} in {}'), 1+len(pset_l), desc_l[keys_l.index('incl')], desc_l[keys_l.index('fold')])
                       ,what=(0,['1']*len(keys_l))), focus_cid='name')
        pass;                  #LOG and log('vals={}',vals)
        if btn is None or btn=='-': return None
        ps_name = vals['name']
        sl,vals = vals['what']
        pass;                  #LOG and log('vals={}',vals)
        ps      = odict([('name',ps_name)])
        stores['pset_nnus'] += 1
        ps['nnus'] = stores['pset_nnus']
        for i, k in enumerate(keys_l):
            if vals[i]=='1':
                ps['_'+k] = 'x'
                ps[    k] = invl_l[i]
            else:
                ps['_'+k] = '-'
        pass;                  #LOG and log('ps={}',(ps))
        pset_l += [ps]
        stores_main.update(stores)
        open(CFG_JSON, 'w').write(json.dumps(stores_main, indent=4))
        app.msg_status(_('Options is saved to preset: ')+ps['name'])
        return None
    
    return      ouvl_l
   #def dlg_press

RE_DOC_REF  = 'https://docs.python.org/3/library/re.html'
_TIPS_BODY  = _(r'''
• ".*" - Option "Regular Expression". 
It allows to use in field "Find what" special symbols:
    .   any character
    \d  digit character (0..9)
    \w  word-like character (digits, letters, "_")
In field "Replace with":
    \1  to insert first found group,
    \2  to insert second found group, ... 
See full documentation by link at bottom.
 
• "aA" - Option "Case sensative"
 
• "w" - {word}
 
—————————————————————————————————————————————— 
 
• Values in fields "In files" and "Not in files" can contain
    ?       for any single char,
    *       for any substring (may be empty),
    [seq]   any character in seq,
    [!seq]  any character not in seq. 
Note: 
    *       matchs all names, 
    *.*     doesnt match all.
 
• Values in fields "In files" and "Not in files" can filter subfolder names if they start with "/".
Example.
    In files:       /a*  *.txt
    Not in files:   /ab*
    In folder:      c:/root
    In subfolders:  All
    Search will consider all *.txt files in folder c:/root
    and in all subfolders a* except ab*.
 
• Set special value "{tags}" for field "In folder" to search in opened documents.
Preset "In folder={tags}" helps to do this.
Fields "In files" and "Not in files" will be to filter tab titles.
To search in all tabs, use mask "*" in field "In files".
 
—————————————————————————————————————————————— 
 
• Long-term searches can be interrupted by ESC.
Search has three stages: 
    picking files, 
    finding fragments, 
    reporting.
ESC stops any stage. When picking and finding, ESC stops only this stage, so next stage begins.
''')
_KEYS_BODY  = _(r'''
• "Find" - {find}
 
• "Replace" - {repl}
 
• "Count" - {coun}
 
• "Current folder" - {cfld}
 
• "Browse…" - {brow}
 
• "In subfolders" - {dept}
 
• "Preset…" - {pset}
 
• "More/Less…" - {more}
 
• "Context" - {cntx}
''')
_TREE_BODY  = _(r'''
Option "Tree type" - {shtp}
''')
_OPTS_BODY  = _(r'''
Extra options for "user.json" (needed restart after changing). 
Default values:
    // Use selection-text from current file when dialog opens
    "fif_use_selection_on_start":false,
    
    // Copy options [.*], [aA], ["w"] from CudaText dialog to plugin's dialog
    "fif_use_edfind_opt_on_start":false,
    
    // ESC stops all stages 
    "fif_esc_full_stop":false,
    
    // Close dialog if search has found matches
    "fif_hide_if_success":false,
    // Save report after filling if tab has filename
    "fif_auto_save_if_file":false,
    // Activate tab with report after filling
    "fif_focus_to_rpt":true,
    
    // Save all request details ("Find", "In folder", …) in first line of result file. 
    // The info will be used in command "Repeat search for this report-tab"
    "fif_save_request_to_rpt":false,
    
    // Length of substring (of field "Find") which appears in title of the search result
    "fif_len_target_in_title":10,
    
    // Show report if nothing found
    "fif_report_no_matches":false,
    
    // Option "Show context" appends N nearest lines to reported lines.
    // So, 2*N+1 lines will be reported for each found line.
    "fif_context_width":1,
    // Or N lines before and M lines after for each found line.
    // N or M can be set to 0
    "fif_context_width_before":1,
    "fif_context_width_after":1,
    
    // Style which marks found fragment in report
    // Full form:
    //    "fif_mark_style":{
    //      "color_back":"", 
    //      "color_font":"",
    //      "font_bold":false, 
    //      "font_italic":false,
    //      "color_border":"", 
    //      "borders":{"left":"","right":"","bottom":"","top":""}
    //    },
    //  Color values: "" - skip, "#RRGGBB" - hex-digits
    //  Values for border sides: "solid", "dash", "2px", "dotted", "rounded", "wave"
    "fif_mark_style":{"borders":{"bottom":"dotted"}},
    "fif_mark_true_replace_style":{"borders":{"bottom":"solid"}},
    "fif_mark_false_replace_style":{"borders":{"bottom":"wave"},"color_border":"#777"},
    
    // Default encoding to read files
    "fif_locale_encoding":"{def_enco}",
    
    // List of lexer names for report. First available lexer will be used.
    "fif_lexers":["Search results"],
    
    // Skip too big files (0 - don't skip)
    "fif_skip_file_size_more_Kb":0,
    
    // Size of buffer (at file start) to detect binary files
    "fif_read_head_size(bytes)":1024,
''')

def dlg_help(word_h, shtp_h, cntx_h, find_h,repl_h,coun_h,cfld_h,brow_h,dept_h,pset_h,more_h,cust_h, stores=None):
    stores      = {} if stores is None else stores
    TIPS_BODY   =_TIPS_BODY.strip().format(word=word_h.replace('\r', '\n'), tags=IN_OPEN_FILES)
    KEYS_BODY   =_KEYS_BODY.strip().format(find=find_h.replace('\r', '\n')
                                          ,repl=repl_h.replace('\r', '\n')
                                          ,coun=coun_h.replace('\r', '\n')
                                          ,cfld=cfld_h.replace('\r', '\n')
                                          ,brow=brow_h.replace('\r', '\n')
                                          ,dept=dept_h.replace('\r', '\n')
                                          ,pset=pset_h.replace('\r', '\n')
                                          ,more=more_h.replace('\r', '\n')
                                          ,cntx=cntx_h.replace('\r', '\n')
                                          )
    TREE_BODY   =_TREE_BODY.strip().format(shtp=shtp_h.replace('\r', '\n'))
    OPTS_BODY   =_OPTS_BODY.strip().replace('{def_enco}', DEF_LOC_ENCO)
    pass;                      #TIPS_BODY='tips';KEYS_BODY='keys';TREE_BODY='tree';OPTS_BODY='opts'
    DW, DH      = 830, 600
    hints_png   = os.path.dirname(__file__)+os.sep+r'images/fif-hints_820x400.PNG'
    tab                 = stores.get('tab', 'keys')

    def prep(tab):
        htxt            = KEYS_BODY            if tab=='keys' else \
                          TIPS_BODY            if tab=='tips' else \
                          TREE_BODY            if tab=='tree' else \
                          OPTS_BODY            if tab=='opts' else ''
        me_t            = GAP       +( 400+GAP if tab=='keys' else 0)
        me_h            = DH-28     +(-400-GAP if tab=='keys' else 0)
        return htxt, me_t, me_h
       #def prep
       
    def when_resize(ag):
        f_wh    = ag.fattrs(attrs=('w', 'h'), live=ag.fattr('vis'))
        return {'ctrls':[('htxt',dict(
                                w=f_wh['w']-10 
                               ,t=5              + (5+400 if tab=='keys' else 0)
                               ,h=f_wh['h']-10-28- (5+400 if tab=='keys' else 0)
                               ))]}

    def acts(aid, ag):
        nonlocal tab
        if aid=='-':                    return None
        if aid=='prps': dlg_fif_opts(); return {}
        stores['tab']   = tab = aid
        htxt, me_t, me_h= prep(tab)
        me_thw          = odict(when_resize(ag)['ctrls'])['htxt']
        return  {'ctrls':
                    [('imge' ,dict(vis=(tab=='keys')        ))
                    ,('htxt' ,dict(val=htxt     ,y=me_thw['t'],h=me_thw['h'],w=me_thw['w'] ))
                    ,('porg' ,dict(vis=(tab=='tips')        ))
                    ,('prps' ,dict(vis=(tab=='opts')        ))
                    ,('keys' ,dict(val=(tab=='keys')        ))
                    ,('tips' ,dict(val=(tab=='tips')        ))
                    ,('tree' ,dict(val=(tab=='tree')        ))
                    ,('opts' ,dict(val=(tab=='opts')        ))
                    ]
                 ,'fid':'htxt'}
       #def acts

    htxt, me_t, me_h    = prep(tab)
    DlgAgent( form  =dict( cap      =_('Help for "Find in Files"')
                          ,w        = GAP+DW+GAP
                          ,h        = GAP+DH+GAP
                          ,resize   = True
                          ,on_resize= when_resize
                          )
            , ctrls = 
                [('imge',dict(tp='im'   ,t=GAP ,h=400   ,l=GAP          ,w=820  ,a='-'      ,items=hints_png            ,vis=(tab=='keys')              ))
                ,('htxt',dict(tp='me'   ,t=me_t,h=me_h  ,l=GAP          ,w=DW               ,ro_mono_brd='1,1,1'        ,val=htxt                       ))
                ,('porg',dict(tp='llb'  ,tid='-'        ,l=GAP          ,w=180  ,a='TB'     ,cap=_('Reg.ex. on python.org')
                                                                                            ,url=RE_DOC_REF             ,vis=(tab=='tips')              ))
                ,('prps',dict(tp='bt'   ,tid='-'        ,l=GAP          ,w=130  ,a='TB'     ,cap=_('&Edit options…')    ,vis=(tab=='opts')  ,call=acts  ))# &e
                ,('keys',dict(tp='chb'  ,tid='-'        ,l=GAP+DW-435   ,w=80   ,a='TB'     ,cap=_('&Keys')             ,val=(tab=='keys')  ,call=acts  ))# &k
                ,('tips',dict(tp='chb'  ,tid='-'        ,l=GAP+DW-350   ,w=80   ,a='TB'     ,cap=_('T&ips')             ,val=(tab=='tips')  ,call=acts  ))# &i
                ,('tree',dict(tp='chb'  ,tid='-'        ,l=GAP+DW-265   ,w=80   ,a='TB'     ,cap=_('&Tree')             ,val=(tab=='tree')  ,call=acts  ))# &t
                ,('opts',dict(tp='chb'  ,tid='-'        ,l=GAP+DW-180   ,w=80   ,a='TB'     ,cap=_('&Opts')             ,val=(tab=='opts')  ,call=acts  ))# &o
                ,('-'   ,dict(tp='bt'   ,t=GAP+DH-23    ,l=GAP+DW-80    ,w=80   ,a='LRTB'   ,cap=_('&Close')                                ,call=acts  ))# &c
            ]
            , fid   = 'htxt'
                               #,options={'gen_repro_to_file':'repro_dlg_help.py'}
        ).show()    #NOTE: dlg_valign
    return stores
   #def dlg_help

mask_h  = _('Space-separated file or folder masks.'
            '\rFolder mask starts with "/".'
            '\rDouble-quote mask, which needs space-char.'
            '\rUse ? for any character and * for any fragment.'
            '\rNote: "*" matchs all names, "*.*" doesnt match all.')
reex_h  = _('Regular expression'
            '\rFormat for found groups in Replace: \\1'
            )
case_h  = _('Case sensative')
word_h  = _('Option "Whole words". It is ignored when:'
            '\r  Regular expression (".*") is turned on,'
            '\r  "Find what" contains not only letters, digits and "_".'
            )
brow_h  = _('Choose folder.'
            '\rShift+Click - Choose file to find in it.'
            )
dept_h  = _('Which subfolders will be used to search.'
            '\rAlt+L - Apply "All".'
            '\rAlt+Y - Apply "In folder only".'
            )
cfld_h  = _('Use folder of current file.'
            '\rShift+Click - Prepare search in the current file.'
            '\rCtrl+Click   - Prepare search in all tabs.'
            '\rCtrl+Shift+Click - Prepare search in the current tab.'
            )
more_h  = _('Show/Hide advanced options'
            '\rCtrl+Click   - Show/Hide "Not in files".'
            '\rShift+Click - Show/Hide "Replace".'
            '\rAlt+V - Toggle visibility on cycle'
            '\r   Hidden "Not in files", hidden  "Replace"'
            '\r   Visible  "Not in files", hidden  "Replace"'
            '\r   Visible  "Not in files", visible   "Replace"'
            '\r   Hidden "Not in files", visible   "Replace"'
            )
cust_h  = _('Change dialog layout')
frst_h  = _('M[, F]'
            '\rStop after M fragments will be found.'
            '\rSearch only inside F first proper files.'
            '\r    Note: If Sort is on then steps are'
            '\r     - Collect all proper files'
            '\r     - Sort the list'
            '\r     - Use first F files to search'
            )
shtp_h  = f(_(  'Format of the reported tree structure.'
            '\rCompact - report all found line with full file info:'
            '\r    path(r[:c:l]):line'
            '\r    path/(r[:c:l]):line'
            '\r  Tree schemes'
            '\r    +Search for "*"'
            '\r      <full_path(row[:col:len])>: line with ALL marked fragments'
            '\r    +Search for "*"'
            '\r      <full_path>: #count'
            '\r         <(row[:col:len])>: line with ALL marked fragments'
            '\rSparse - report separated folders and fragments:'
            '\r    dir/file(r[:c:l]):line'
            '\r    dir/file/(r[:c:l]):line'
            '\r  Tree schemes'
            '\r    +Search for "*"'
            '\r      <root>: #count'
            '\r        <dir>: #count'
            '\r          <file.ext(row[:col:len])>: line with ONE marked fragment'
            '\r    +Search for "*"'
            '\r      <root>: #count'
            '\r        <dir>: #count'
            '\r          <file.ext>: #count'
            '\r            <(row[:col:len])>: line with ONE marked fragment'
            '\rFor '
            '\r  sorted files'
            '\rand'
            '\r  In folder={}'
            '\ronly Compact options are used.'
           ),IN_OPEN_FILES)
cntx_h  = _('Show result line and both its nearest lines, above and below result'
            '\rCtrl+Click  - Set count of above and below lines.')
algn_h  = _("Align columns (filenames/numbers) by widest cell width")
find_h  = f(_('Start search.'
            '\rShift+Click  - Put report to new tab.'
            '\r   It is like pressing Find with option "Show in: {}".'
            '\rCtrl+Click  - Append result to existing report.'
            '\r   It is like pressing Find with option "[x]Append results".'
            ), TOTB_NEW_TAB)
repl_h  = _('Start search and replacement.'
            '\rShift+Click  - Run without question'
            '\r   "Do you want to replace…?"'
            )
coun_h  = _('Count matches only.'
            '\rShift+Click  - Find file names only.'
            )
pset_h  = _('Save options for future. Restore saved options.'
            '\rShift+Click - Show preset list in applying history order.'
            '\rCtrl+Click   - Apply last used preset.'
            '\rAlt+1 - Apply first preset.'
            '\rAlt+2 - Apply second preset.'
            '\rAlt+3 - Apply third preset.'
            )
    
enco_h  = f(_('In which encodings try to read files.'
            '\rFirst suitable will be used.'
            '\r"{}" is slow.'
            '\r '
            '\rDefault encoding: {}'), ENCO_DETD, loc_enco)

def add_to_history(val:str, lst:list, max_len:int, unicase=True)->list:
    """ Add/Move val to list head. """
    pass;                  #LOG and log('val, lst={}',(val, lst))
    lst_u = [ s.upper() for s in lst] if unicase else lst
    val_u = val.upper()               if unicase else val
    if val_u in lst_u:
        if 0 == lst_u.index(val_u):   return lst
        del lst[lst_u.index(val_u)]
    lst.insert(0, val)
    pass;                  #LOG and log('lst={}',lst)
    if len(lst)>max_len:
        del lst[max_len:]
    pass;                  #LOG and log('lst={}',lst)
    return lst
   #def add_to_history

def get_live_fiftabs(_fxs)->list:
    rsp = []
    for h in app.ed_handles():
        try_ed  = app.Editor(h)
        try_fn  = try_ed.get_filename()
        if try_fn in _fxs:
            continue
        tag     = try_ed.get_prop(app.PROP_TAG)
        lxr     = try_ed.get_prop(app.PROP_LEXER_FILE)
        if False:pass
        elif lxr.upper() in lexers_l:
            rsp+= ['tab:'+try_ed.get_prop(app.PROP_TAB_TITLE)]
        elif tag.startswith('FiF'):
            rsp+= ['tab:'+try_ed.get_prop(app.PROP_TAB_TITLE)]
    return rsp
   #def get_live_fiftabs
    
def dlg_fif(what='', opts={}):
    return FifD(what, opts).show()

class FifD:
    
    @staticmethod
    def scam_pair(aid):
        scam        = app.app_proc(app.PROC_GET_KEYSTATE, '')
        return aid, scam + '/' + aid if scam and scam!='a' else aid   # smth == a/smth

    @staticmethod
    def upgrade(dct):
        if 'totb' in dct:
            dct['totb']  = int(dct['totb'])

    @staticmethod
    def get_totb_l(fxs):
        tofx_l      = [f('file:{1}'+' '*100+'{0}'
                        , *os.path.split(fx)) 
                      for fx in fxs if os.path.isfile(fx) ]    # ' '*100 to hide folder in list-/combo-boxes
        return        TOTB_L                    \
                    + [_('[Clear fixed files]')
                      ,_('[Add fixed file]')]   \
                    + tofx_l                    \
                    + get_live_fiftabs(fxs)

    WIN_MAC     = (get_desktop_environment() in ('win', 'mac'))
    EG0,EG1,EG2,EG3,EG4,EG5,EG6,EG7,EG8,EG9,EG10 = [0]*11 if WIN_MAC else [5*i for i in range(11)]
    DLG_W0,     \
    DLG_H0      = (700, 335 + EG1 + EG10)
    DEF_WD_TXTS = 300
    DEF_WD_BTNS = 100

    TXT_W       = DEF_WD_TXTS
    BTN_W       = DEF_WD_BTNS
    LBL_L       = GAP+38*3+GAP+25
    CMB_L       = LBL_L+100
    TL2_L       = LBL_L+220-85
    TBN_L       = CMB_L+TXT_W+GAP

    def show(self):
        self.pre_cnts()
        DlgAgent(
            form =dict(cap     = self.get_fif_cap()
                      ,resize  = True
                      ,w       = self.dlg_w
                      ,h       = self.dlg_h,   h_max   = self.dlg_h
                      )
        ,   ctrls=self.get_fif_cnts()
        ,   vals =self.get_fif_vals()
        ,   fid  ='what'
        ,   options = {'bindof':self}
        ).show(callbk_on_exit=self.copy_vals)
        self.store()
       #def show

    def __init__(self, what='', opts={}):
        pass
        pass;                  #LOG and log('FifD.DEF_WD_TXTS={}',(FifD.DEF_WD_TXTS))
        self.stores  = json.loads(open(CFG_JSON).read(), object_pairs_hook=odict) \
                        if os.path.exists(CFG_JSON) and os.path.getsize(CFG_JSON) != 0 else \
                       odict()
        FifD.upgrade(self.stores)     # Upgrade types
    
        self.what_s  = what if what else ed.get_text_sel() if USE_SEL_ON_START else ''
        self.what_s  = self.what_s.splitlines()[0] if self.what_s else ''
        self.repl_s  = opts.get('repl', '')
        self.reex01  = opts.get('reex', self.stores.get('reex', '0'))
        self.case01  = opts.get('case', self.stores.get('case', '0'))
        self.word01  = opts.get('word', self.stores.get('word', '0'))
        if USE_EDFIND_OPS:
            ed_opt  = CdSw.app_proc(CdSw.PROC_GET_FIND_OPTIONS, '')
            # c - Case, r - RegEx,  w - Word,  f - From-caret,  a - Wrap
            self.reex01  = '1' if 'r' in ed_opt else '0'
            self.case01  = '1' if 'c' in ed_opt else '0'
            self.word01  = '1' if 'w' in ed_opt else '0'
        self.incl_s  = opts.get('incl', self.stores.get('incl',  [''])[0])
        self.excl_s  = opts.get('excl', self.stores.get('excl',  [''])[0])
        self.fold_s  = opts.get('fold', self.stores.get('fold',  [''])[0])
        self.dept_n  = opts.get('dept', self.stores.get('dept',  0)-1)+1
        self.join_s  = opts.get('join', self.stores.get('join', '0'))
        self.totb_i  = opts.get('totb', self.stores.get('totb',  0 ));  self.totb_i =  1  if self.totb_i== 0  else self.totb_i
        self.shtp_s  = opts.get('shtp', self.stores.get('shtp', '0'))
        self.cntx_s  = opts.get('cntx', self.stores.get('cntx', '0'))
        self.algn_s  = opts.get('algn', self.stores.get('algn', '0'))
        self.skip_s  = opts.get('skip', self.stores.get('skip', '0'))
        self.sort_s  = opts.get('sort', self.stores.get('sort', '0'))
        self.frst_s  = opts.get('frst', self.stores.get('frst', '0'));  self.frst_s  = '0' if not self.frst_s else self.frst_s
        self.enco_s  = opts.get('enco', self.stores.get('enco', '0'))

        self.wo_excl= self.stores.get('wo_excl', True)
        self.wo_repl= self.stores.get('wo_repl', True)
        self.wo_adva= self.stores.get('wo_adva', True)

        self.caps    = None     # Will be filled in get_fif_cnts

        self.what_l  = None     # Will be filled in pre_cnts
        self.incl_l  = None     # Will be filled in pre_cnts
        self.excl_l  = None     # Will be filled in pre_cnts
        self.fold_l  = None     # Will be filled in pre_cnts
        self.repl_l  = None     # Will be filled in pre_cnts
        self.totb_l  = None     # Will be filled in pre_cnts
        self.gap1    = None     # Will be filled in pre_cnts
        self.gap2    = None     # Will be filled in pre_cnts
        self.gap3    = None     # Will be filled in pre_cnts
        self.dlg_w   = None     # Will be filled in pre_cnts
        self.dlg_h   = None     # Will be filled in pre_cnts
       #def __init__
    
    def copy_vals(self, ag):
        self.reex01     = ag.cval('reex')
        self.case01     = ag.cval('case')
        self.word01     = ag.cval('word')
        self.what_s     = ag.cval('what')
        self.incl_s     = ag.cval('incl')
        if not self.wo_excl:     
            self.excl_s = ag.cval('excl')
        else:
            self.excl_s = ''
        self.fold_s     = ag.cval('fold')
        self.dept_n     = ag.cval('dept')
        if not self.wo_repl:     
            self.repl_s = ag.cval('repl')
        if not self.wo_adva:     
            self.join_s = ag.cval('join')
            self.totb_i = ag.cval('totb')
            self.shtp_s = ag.cval('shtp')
            self.cntx_s = ag.cval('cntx')
            self.algn_s = ag.cval('algn')
            self.skip_s = ag.cval('skip')
            self.sort_s = ag.cval('sort')
            self.frst_s = ag.cval('frst')
            self.enco_s = ag.cval('enco')
       #def copy_vals
    
    def store(self, save=True, set=''):
        if save:
            self.stores['wo_adva']  = self.wo_adva
            self.stores['wo_excl']  = self.wo_excl
            self.stores['wo_repl']  = self.wo_repl
            self.stores['reex']     = self.reex01
            self.stores['case']     = self.case01
            self.stores['word']     = self.word01
            self.stores['what']     = add_to_history(self.what_s, self.stores.get('what', []), MAX_HIST, unicase=False)
            self.stores['incl']     = add_to_history(self.incl_s, self.stores.get('incl', []), MAX_HIST, unicase=(os.name=='nt'))
            self.stores['excl']     = add_to_history(self.excl_s, self.stores.get('excl', []), MAX_HIST, unicase=(os.name=='nt'))
            self.stores['fold']     = add_to_history(self.fold_s, self.stores.get('fold', []), MAX_HIST, unicase=(os.name=='nt'))
            self.stores['dept']     = self.dept_n
            self.stores['repl']     = add_to_history(self.repl_s, self.stores.get('repl', []), MAX_HIST, unicase=False)
            self.stores['join']     = self.join_s
            self.stores['totb']     = 1 if self.totb_i==0 else self.totb_i
            self.stores['shtp']     = self.shtp_s
            self.stores['cntx']     = self.cntx_s
            self.stores['algn']     = self.algn_s
            self.stores['skip']     = self.skip_s
            self.stores['sort']     = self.sort_s
            self.stores['frst']     = self.frst_s
            self.stores['enco']     = self.enco_s
            open(CFG_JSON, 'w').write(json.dumps(self.stores, indent=4))
       #def store
    
    def pre_cnts(self):
        self.what_l = [s for s in self.stores.get('what', []) if s ]
        self.incl_l = [s for s in self.stores.get('incl', []) if s ]
        self.excl_l = [s for s in self.stores.get('excl', []) if s ]
        self.fold_l = [s for s in self.stores.get('fold', []) if s ]
        self.repl_l = [s for s in self.stores.get('repl', []) if s ]
        self.totb_l = FifD.get_totb_l(self.stores.get('tofx', []))
        
#       self.wo_excl= self.stores.get('wo_excl', True)
#       self.wo_repl= self.stores.get('wo_repl', True)
#       self.wo_adva= self.stores.get('wo_adva', True)
        self.gap1   = (GAP- 28 if self.wo_repl else GAP)
        self.gap2   = (GAP- 28 if self.wo_excl else GAP)+self.gap1 -GAP
        self.gap3   = (GAP-132 if self.wo_adva else GAP)+self.gap2 -GAP
        self.dlg_w,\
        self.dlg_h  = (self.TBN_L+FifD.BTN_W+GAP, FifD.DLG_H0+self.gap3-(15+FifD.EG4 if self.wo_adva else 15))
        pass;                  #LOG and log('gap2={}',(self.gap2))
        pass;                  #LOG and log('dlg_w, dlg_h={}',(self.dlg_w, self.dlg_h))
        return self
       #def pre_cnts

    def get_fif_cap(self):
        return f(_('Find in Files{} ({})')
               , '' if not self.wo_adva else  ' [' + (''
                                +   (_(SHTP_L[int(self.shtp_s)]+', ')                   )
                                +   (_('Append, ')                if self.join_s=='1' else '')
                                +   (_('Context, ')               if self.cntx_s=='1' else '')
                                +   (_('Sorted, ')                if self.sort_s!='0' else '')
                                +   (_('First ')+self.frst_s+', ' if self.frst_s!='0' else '')
                                ).rstrip(', ') + ']'
               , VERSION_V)

    def do_focus(self,aid,ag, store=True):
        self.store() if store else None
        aid_ed  = ag.cattr(aid, 'type') in ('edit', 'combo')
        fid     = ag.fattr('focused')
        fid_ed  = ag.cattr(fid, 'type') in ('edit', 'combo')
        fid     = aid    if aid_ed                                  else \
                  fid    if fid_ed                                  else \
                  'what' if aid in ('brow', 'cfld')                 else \
                  'what'
        return {'fid':fid}
       #def do_focus
    
    def do_pres(self, aid, ag):
        if aid not in ('prs1', 'prs2', 'prs3', 'pres'): return self.do_focus(aid,ag)
        btn_p,btn_m = FifD.scam_pair(aid)
        
        if btn_p in ('prs1', 'prs2', 'prs3') \
        or btn_m=='c/pres': # Ctrl+Preset - Apply last used preset
            pset_l  = self.stores.setdefault('pset', [])
            if not pset_l:
                return self.do_focus(aid,ag)   #continue#while_fif
            ps  = sorted(pset_l, key=lambda ps: ps.get('nnus', 0), reverse=True)[0] \
                    if btn_m=='c/pres'                      else \
                  pset_l[0] \
                    if btn_p=='prs1'                        else \
                  pset_l[1] \
                    if btn_p=='prs2' and len(pset_l)>1 else \
                  pset_l[2] \
                    if btn_p=='prs3' and len(pset_l)>2 else \
                  None
            if not ps:
                return self.do_focus(aid,ag)   #continue#while_fif
            FifD.upgrade(ps)
            self.reex01  = ps['reex'] if ps.get('_reex', '')=='x' else self.reex01
            self.case01  = ps['case'] if ps.get('_case', '')=='x' else self.case01
            self.word01  = ps['word'] if ps.get('_word', '')=='x' else self.word01
            self.incl_s  = ps['incl'] if ps.get('_incl', '')=='x' else self.incl_s
            self.excl_s  = ps['excl'] if ps.get('_excl', '')=='x' else self.excl_s
            self.fold_s  = ps['fold'] if ps.get('_fold', '')=='x' else self.fold_s
            self.dept_n  = ps['dept'] if ps.get('_dept', '')=='x' else self.dept_n
            self.skip_s  = ps['skip'] if ps.get('_skip', '')=='x' else self.skip_s
            self.sort_s  = ps['sort'] if ps.get('_sort', '')=='x' else self.sort_s
            self.frst_s  = ps['frst'] if ps.get('_frst', '')=='x' else self.frst_s
            self.enco_s  = ps['enco'] if ps.get('_enco', '')=='x' else self.enco_s
            self.totb_i  = ps['totb'] if ps.get('_totb', '')=='x' else self.totb_i
            self.join_s  = ps['join'] if ps.get('_join', '')=='x' else self.join_s
            self.shtp_s  = ps['shtp'] if ps.get('_shtp', '')=='x' else self.shtp_s
            self.algn_s  = ps['algn'] if ps.get('_algn', '')=='x' else self.algn_s
            self.cntx_s  = ps['cntx'] if ps.get('_cntx', '')=='x' else self.cntx_s
            app.msg_status(_('Options is restored from preset: ')+ps['name'])

        if btn_m=='pres' \
        or btn_m=='s/pres': # Shift+Preset - Show list in history order
#           ag.bind_do(['totb'])
#           ag.bind_do()
            self.copy_vals(ag)
            onof        = {'0':'Off', '1':'On'}
#           totb_i      = int(totb_s)
            self.totb_i = self.totb_i if 0<self.totb_i<4+len(self.stores.get('tofx', [])) else 1   # "tab:" skiped
            totb_v      = self.totb_l[self.totb_i]
            ans     = dlg_press(self.stores, btn_m=='s/pres',
                       (self.reex01,self.case01,self.word01,
                        self.incl_s,self.excl_s,
                        self.fold_s,self.dept_n,
                        self.skip_s,self.sort_s,self.frst_s,self.enco_s,
                        totb_v,     self.join_s,self.shtp_s,self.algn_s,self.cntx_s),
                       (onof[self.reex01],onof[self.case01],onof[self.word01],
                        '"'+self.incl_s+'"','"'+self.excl_s+'"',
                        '"'+self.fold_s+'"',DEPT_L[self.dept_n],
                        SKIP_L[int(self.skip_s)],SORT_L[int(self.sort_s)],self.frst_s,ENCO_L[int(self.enco_s)],
                        totb_v,onof[self.join_s],SHTP_L[int(self.shtp_s)],onof[self.algn_s],onof[self.cntx_s])
                        )
            ag.activate()
            if ans is None:
                return self.do_focus(aid,ag)   #continue#while_fif
            (           self.reex01,self.case01,self.word01,
                        self.incl_s,self.excl_s,
                        self.fold_s,self.dept_n,
                        self.skip_s,self.sort_s,self.frst_s,self.enco_s,
                        totb_v,     self.join_s,self.shtp_s,self.algn_s,self.cntx_s)  = ans
            self.totb_i = self.totb_l.index(totb_v) if totb_v in self.totb_l   else \
                          totb_v                    if totb_v in ('0', '1')    else \
                          1
        
#       self.store() # in do_focus
        return (dict(vals=self.get_fif_vals()
                    ,form={'cap':self.get_fif_cap()}
                    )
               ,self.do_focus(aid,ag)
               )
       #def do_pres

    def do_fold(self, aid, ag):
        self.copy_vals(ag)
#       ag.bind_do()
#       ag.bind_do(['excl','fold','dept'])
        btn_p,btn_m = FifD.scam_pair(aid)

        if False:pass
        elif btn_m=='brow':     # BroDir
            path        = CdSw.dlg_dir(os.path.expanduser(self.fold_s))
            if not path: return self.do_focus(aid,ag)   #continue#while_fif
            self.fold_s = path
            self.fold_s = self.fold_s.replace(os.path.expanduser('~'), '~', 1)      \
                            if self.fold_s.startswith(os.path.expanduser('~')) else \
                          self.fold_s
#           self.focused= 'fold'
        elif btn_m=='s/brow':   # [Shift+]BroDir = BroFile
            fn          = app.dlg_file(True, '', os.path.expanduser(self.fold_s), '')
            if not fn or not os.path.isfile(fn):    return self.do_focus(aid,ag)   #continue#while_fif
            self.incl_s = os.path.basename(fn)
            self.fold_s = os.path.dirname(fn)
            self.fold_s = self.fold_s.replace(os.path.expanduser('~'), '~', 1)      \
                            if self.fold_s.startswith(os.path.expanduser('~')) else \
                          self.fold_s
        elif btn_m=='cfld' and ed.get_filename():
            self.fold_s = os.path.dirname(ed.get_filename())
            self.fold_s = self.fold_s.replace(os.path.expanduser('~'), '~', 1)      \
                            if self.fold_s.startswith(os.path.expanduser('~')) else \
                          self.fold_s
        elif btn_m=='s/cfld':   # [Shift+]CurDir = CurFile
            if not os.path.isfile(     ed.get_filename()):   return self.do_focus(aid,ag)   #continue#while_fif
            self.incl_s = os.path.basename(ed.get_filename())
            self.fold_s = os.path.dirname( ed.get_filename())
            self.fold_s = self.fold_s.replace(os.path.expanduser('~'), '~', 1)      \
                            if self.fold_s.startswith(os.path.expanduser('~')) else \
                          self.fold_s
            self.dept_n = 1
            self.excl_s = ''
        elif btn_m=='c/cfld':   # [Ctrl+]CurDir  = InTabs
            self.incl_s = '*'
            self.fold_s = IN_OPEN_FILES
        elif btn_m=='sc/cfld':  # [Ctrl+Shift+]CurDir = CurTab
            self.incl_s = ed.get_prop(app.PROP_TAB_TITLE)   ##!! need tab-id?
            self.fold_s = IN_OPEN_FILES
            self.excl_s = ''

#       self.store() # in do_focus
        return (dict(vals=self.get_fif_vals())
               ,self.do_focus(aid,ag)
               )
       #def do_fold
       
    def do_dept(self, aid, ag):
        self.copy_vals(ag)
#       ag.bind_do(['dept'])
        pass;                  #LOG and log('self.dept_n={}',(repr(self.dept_n)))
        self.dept_n = 0 if aid=='depa' else \
                      1 if aid=='depo' else \
                      self.dept_n
#       self.store() # in do_focus
        return (dict(vals={'dept':self.dept_n})
               ,self.do_focus(aid,ag)
               )
       #def do_dept
    
    def do_more(self, aid, ag):
        self.copy_vals(ag)
#       ag.bind_do()
#       ag.bind_do(['excl','repl','adva'])
        btn_p,btn_m = FifD.scam_pair(aid)

        if False:pass
        elif btn_m=='more':
            self.wo_adva    = not self.wo_adva

        elif btn_m=='c/more':     # [Ctrl+]More       = show/hide excl
            self.wo_excl    = not selfwo_excl
        elif btn_m=='s/more':     # [Shift+]More      = show/hide repl
            self.wo_repl    = not self.wo_repl

        elif btn_p=='loop':
            v_excl = not self.wo_excl
            v_repl = not self.wo_repl
            (v_excl,v_repl) = (T,F) if (v_excl,v_repl)==(F,F) else \
                              (T,T) if (v_excl,v_repl)==(T,F) else \
                              (F,T) if (v_excl,v_repl)==(T,T) else \
                              (F,F) if (v_excl,v_repl)==(F,T) else (v_excl,v_repl)
            self.wo_excl    = not v_excl
            self.wo_repl    = not v_repl
        elif btn_m=='c/cust':     # [Ctrl+]Adjust  = dlg_valign_consts
            dlg_valign_consts()
        elif btn_m=='cust':
            shex_c  = f(_('Show "&{}"')                          , self.caps['excl'])
            shre_c  = f(_('Show "&{}" and "{}"')                 , self.caps['repl'], self.caps['!rep'])
            aid_,vals,*_t   = dlg_wrapper(_('Adjust dialog controls'), GAP+290+GAP,GAP+90+GAP,      #NOTE: dlg-cust
                 [dict(cid='shex',tp='ch'    ,t=GAP             ,l=GAP          ,w=150  ,cap=shex_c                                     ) # &n
                 ,dict(cid='shre',tp='ch'    ,t=GAP+ 30         ,l=GAP          ,w=150  ,cap=shre_c                                     ) # &r
                 ,dict(cid='!'   ,tp='bt'    ,t=GAP+ 90-28      ,l=GAP+290-170  ,w=80   ,cap=_('OK')    ,def_bt=True                    ) # 
                 ,dict(cid='-'   ,tp='bt'    ,t=GAP+ 90-28      ,l=GAP+290-80   ,w=80   ,cap=_('Cancel')                                )
                 ],    dict(shex=not self.wo_excl
                           ,shre=not self.wo_repl
                           ), focus_cid='wdtx')
            pass;              #LOG and log('vals={}',vals)
            if aid_ is None or aid_=='-': return self.do_focus(aid,ag)   #continue#while_fif
            self.wo_excl    = not vals['shex']
            self.wo_repl    = not vals['shre']
        else:
            return self.do_focus(aid,ag)
        
#       self.store() # in do_focus
#       open(CFG_JSON, 'w').write(json.dumps(self.stores, indent=4))
        self.pre_cnts()
        pass;                  #LOG and log('dlg_h={}',(dlg_h))
        return (dict(form =dict( cap  =self.get_fif_cap()
                                ,h    =self.dlg_h
                                ,h_min=self.dlg_h
                                ,h_max=self.dlg_h
                                )
                    ,vals =self.get_fif_vals()
#                   ,ctrls=self.get_fif_cnts())
                    ,ctrls=self.get_fif_cnts('vis+pos'))
               ,self.do_focus(aid,ag)
               )
       #def do_more

    def do_cntx(self, aid, ag):
#       ag.bind_do(['cntx'])
        self.copy_vals(ag)
        btn_p,btn_m = FifD.scam_pair(aid)
        if btn_m=='c/cntx' and self.cntx_s=='1':    # '1'? so 
            sBf = str(apx.get_opt('fif_context_width_before', apx.get_opt('fif_context_width', 1)))
            sAf = str(apx.get_opt('fif_context_width_after' , apx.get_opt('fif_context_width', 1)))
            ans   = app.dlg_input_ex(2, _('Report context settings')
                , _('Report with lines before') , sBf
                , _('Report with lines after')  , sAf
                )
            pass;              #LOG and log('cntx ans={}',(ans))
            sBf,sAf = ans   if ans is not None else     ('0', '0')
            pass;              #LOG and log('cntx sBf,sAf={}',(sBf,sAf))
            nBf = int(sBf) if sBf.isdigit() else 0
            nAf = int(sAf) if sAf.isdigit() else 0
            pass;              #LOG and log('cntx nBf,nAf={}',(nBf,nAf))
            if nBf+nAf > 0:
                apx.set_opt('fif_context_width_before', nBf)
                apx.set_opt('fif_context_width_after' , nAf)
#       self.store() # in do_focus
        return self.do_focus(aid,ag)
       #def do_cntx

    def do_totb(self, aid, ag):
        pass;                  #LOG and log('totb props={}',(ag.cattrs('totb')))
        totb_i_pre  = self.totb_i
#       ag.bind_do(['totb', 'fold'])
        self.copy_vals(ag)
        totb_v      = self.totb_l[self.totb_i]
        pass;                   LOG and log('totb_i_pre,totb_i,totb_v={}',(totb_i_pre,self.totb_i,totb_v))
        fxs         = self.stores.get('tofx', [])
        if False:pass
        elif totb_v==_('[Clear fixed files]') and fxs:
            if app.ID_YES == app.msg_box(
                              f(_('Clear all fixed files ({}) for "{}"?'), len(fxs), self.caps['totb'])
                            , app.MB_OKCANCEL+app.MB_ICONQUESTION):
                self.stores['tofx']  = []
                self.totb_i  = 1                                # == TOTB_USED_TAB
            else:
                self.totb_i  = totb_i_pre
                return {'vals':{'totb':self.totb_i}}            # Cancel, set prev state
        elif totb_v==_('[Add fixed file]'):
            fx      = app.dlg_file(True, '', os.path.expanduser(self.fold_s), '')
            if not fx or not os.path.isfile(fx):
                totb_i  = totb_i_pre
                return {'vals':{'totb':totb_i}}                 # Cancel, set prev state
            else:
                fxs     = self.stores.get('tofx', [])
                if fx in fxs:
                    self.totb_i  = 4+fxs.index(fx)
                else:
                    self.stores['tofx'] = fxs + [fx]
                    self.totb_i  = 4+len(self.stores['tofx'])-1 # skip: new,prev,clear,add,files-1
        else:   return self.do_focus(aid,ag)
        
        self.totb_l = FifD.get_totb_l(self.stores.get('tofx', []))
        pass;                   LOG and log('self.totb_i={}',(self.totb_i))
#       self.store() # in do_focus
        return ({'ctrls':[('totb', {'val':self.totb_i ,'items':self.totb_l})]}
               ,self.do_focus(aid,ag)
               ) 
       #def do_totb
       
    def do_help(self, aid, ag):
        self.stores['help.data'] = dlg_help(
            word_h, shtp_h, cntx_h, find_h,repl_h,coun_h,cfld_h,brow_h,dept_h,pset_h,more_h,cust_h
        ,   self.stores.get('help.data'))
        open(CFG_JSON, 'w').write(json.dumps(self.stores, indent=4))
        ag.activate()
        return self.do_focus(aid,ag)
       #def do_help
    
    def do_exit(self, aid, ag):
#       ag.bind_do()
        self.copy_vals(ag)
        pass;                   LOG and log('self.totb_i={}',(self.totb_i))
        self.store()
#       open(CFG_JSON, 'w').write(json.dumps(self.stores, indent=4))
        return None
       #def do_exit
    
    def do_work(self, aid, ag):
#       ag.bind_do()
        self.copy_vals(ag)
#       self.store() # in do_focus
        
        btn_p,btn_m = FifD.scam_pair(aid)
        if btn_p not in ('!cnt', '!fnd', '!rep'):   return self.do_focus(aid,ag)
        
        w_excl      = not self.wo_excl
        self.excl_s = self.excl_s if w_excl else ''
        
        if btn_m=='!rep' \
        and app.ID_OK != app.msg_box(
             f(_('Do you want to replace in {}?'), 
                _('current tab')        if self.fold_s==IN_OPEN_FILES and not ('*' in self.incl_s or '?' in self.incl_s) else 
                _('all tabs')           if self.fold_s==IN_OPEN_FILES else 
                _('all found files')
             )
            ,app.MB_OKCANCEL+app.MB_ICONQUESTION):
            return self.do_focus(aid,ag)

#       fold_s  = ag.cval('fold')
#       what_s  = ag.cval('what')  
#       w_repl  = not stores.get('wo_repl', True)
        w_repl      = not self.wo_repl
        self.repl_s = self.repl_s if w_repl else ''
        
        root        = self.fold_s.rstrip(r'\/') if self.fold_s!='/' else self.fold_s
        root        = os.path.expanduser(root)
        root        = os.path.expandvars(root)
        if not self.what_s:
            app.msg_box(f(_('Fill the "{}" field'), self.caps['what']), app.MB_OK+app.MB_ICONWARNING)
            return {'fid':'what'}
        
#       reex01  = ag.cval('reex')

        if self.reex01=='1':
            try:
                re.compile(self.what_s)
            except Exception as ex:
                app.msg_box(f(_('Set correct "{}" reg.ex.\n\nError:\n{}')
                             , self.caps['what'], ex), app.MB_OK+app.MB_ICONWARNING) 
                return {'fid':'what'}
            if btn_p=='!rep':
                try:
                    re.sub(self.what_s, self.repl_s, '')
                except Exception as ex:
                    app.msg_box(f(_('Set correct "{}" reg.ex.\n\nError:\n{}')
                                 , self.caps['repl'], ex), app.MB_OK+app.MB_ICONWARNING) 
                    return {'fid':'repl'}
        if self.fold_s!=IN_OPEN_FILES and (not root or not os.path.isdir(root)):
            app.msg_box(f(_('Set existing value in "{}"  or use "{}" (see {})')
                         , self.caps['fold'], IN_OPEN_FILES, self.caps['pres']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'fold'}
        if not self.incl_s:
            app.msg_box(f(_('Fill the "{}" field'), self.caps['incl']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'incl'}
        if 0 != self.incl_s.count('"')%2:
            app.msg_box(f(_('Fix quotes in the "{}" field'), self.caps['incl']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'incl'}
        if 0 != self.excl_s.count('"')%2:
            app.msg_box(f(_('Fix quotes in the "{}" field'), self.caps['excl']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'excl'}

#       shtp_s  = ag.cval('shtp', '0')

        if SHTP_L[int(self.shtp_s)] in (SHTP_MIDDL_R, SHTP_MIDDL_RCL
                                       ,SHTP_SPARS_R, SHTP_SPARS_RCL
                                       ) and \
           self.sort_s!='0':
            app.msg_box(f(_('Conflicting "{}" and "{}" options.\n\nSee Help--Tree.')
                         ,self.caps['sort'], self.caps['shtp']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'shtp'}
        if SHTP_L[int(self.shtp_s)] in (SHTP_MIDDL_R, SHTP_MIDDL_RCL
                                       ,SHTP_SPARS_R, SHTP_SPARS_RCL
                                       ) and \
           self.fold_s==IN_OPEN_FILES:
            app.msg_box(f(_('Conflicting "{}" and "{}" options.\n\nSee Help--Tree.')
                         ,IN_OPEN_FILES, self.caps['shtp']), app.MB_OK+app.MB_ICONWARNING) 
            return {'fid':'shtp'}

#       case01  = ag.cval('case')
#       word01  = ag.cval('word')
#       dept_n  = ag.cval('dept')
#       join_s  = ag.cval('join', '0')
#       totb_i  = ag.cval('totb',  1 )
#       cntx_s  = ag.cval('cntx', '0')
#       algn_s  = ag.cval('algn', '0')
#       skip_s  = ag.cval('skip', '0')
#       sort_s  = ag.cval('sort', '0')
#       frst_s  = ag.cval('frst', '0')
#       enco_s  = ag.cval('enco', '0')
        
        pass;                   LOG and log('self.dept_n={}',(repr(self.dept_n)))
        how_walk    =dict(                                  #NOTE: fif params
             root       =root
            ,file_incl  =self.incl_s
            ,file_excl  =self.excl_s
            ,depth      =self.dept_n-1               # ['All', 'In folder only', '1 level', …]
            ,skip_hidn  =self.skip_s in ('1', '3')   # [' ', 'Hidden', 'Binary', 'Hidden, Binary']
            ,skip_binr  =self.skip_s in ('2', '3')   # [' ', 'Hidden', 'Binary', 'Hidden, Binary']
            ,sort_type  =apx.icase( self.sort_s=='0','' 
                                   ,self.sort_s=='1','date,desc' 
                                   ,self.sort_s=='2','date,asc' ,'')
            ,only_frst  =int((self.frst_s+',0').split(',')[1])
            ,skip_unwr  =btn_p=='!rep'
            ,enco       =ENCO_L[int(self.enco_s)].split(', ')
            )
        what_find   =dict(
             find       =self.what_s
            ,repl       =self.repl_s if btn_p=='!rep' else None
            ,mult       =False
            ,reex       =self.reex01=='1'
            ,case       =self.case01=='1'
            ,word       =self.word01=='1'
            ,only_frst  =int((self.frst_s+',0').split(',')[0])
            )
        what_save   = dict(
             count      = btn_m!='s/!cnt'
            ,place      = btn_p!='!cnt'
            ,lines      = btn_p!='!cnt'
            )
        shtp_v      = SHTP_L[int(self.shtp_s)]
        totb_it     = self.totb_l[self.totb_i]
        fxs         = self.stores.get('tofx', [])
        totb_v      = TOTB_NEW_TAB                  if btn_m=='s/!fnd' or totb_it==TOTB_NEW_TAB     else \
                      totb_it                       if totb_it.startswith('tab:')                   else \
                      'file:'+fxs[self.totb_i-4]    if totb_it.startswith('file:')                  else \
                      TOTB_USED_TAB
        pass;               LOG#and log('totb_i,totb_it,totb_v={}',(totb_i,totb_it,totb_v))
        how_rpt     = dict(
             totb   =    totb_v
            ,sprd   =              self.sort_s=='0' and shtp_v not in (SHTP_SHORT_R, SHTP_SHORT_RCL, SHTP_SHRTS_R, SHTP_SHRTS_RCL)
            ,shtp   =    shtp_v if self.sort_s=='0' or  shtp_v     in (SHTP_SHORT_R, SHTP_SHORT_RCL, SHTP_SHRTS_R, SHTP_SHRTS_RCL) else SHTP_SHORT_R
            ,cntx   =    '1'==self.cntx_s and btn_p!='!rep'
            ,algn   =    '1'==self.algn_s
            ,join   =    '1'==self.join_s or  btn_m=='c/!fnd' # Append if Ctrl+Find
            )
    #   totb_s  = '1' if totb_s=='0' else totb_s
        ################################
        progressor = ProgressAndBreak()
        rpt_data, rpt_info = find_in_files(     #NOTE: run-fif
             how_walk   = how_walk
            ,what_find  = what_find
            ,what_save  = what_save
            ,how_rpt    = how_rpt
            ,progressor = progressor
            )
        if not rpt_data and not rpt_info: 
            app.msg_status(_("Search stopped"))
            return self.do_focus(aid,ag)   #continue#while_fif
        frfls   = rpt_info['files']
        frgms   = rpt_info['frgms']
        ################################
        pass;              #LOG and log('frgms={}, rpt_data=\n{}',frgms, pf(rpt_data))
        msg_rpt = _('No matches found') \
                    if 0==frfls else \
                  f(_('Found {} match(es) in {} file(s)'), frgms, frfls)
        progressor.set_progress(msg_rpt)
        if 0==frgms and not REPORT_FAIL:    return self.do_focus(aid,ag)   #continue#while_fif
        req_opts= None
        if SAVE_REQ_TO_RPT:
            req_opts= {k:v for (k,v) in self.stores.items() if k[:3] not in ('wd_', 'wo_', 'pse')}
            req_opts['what']=self.what_s
            req_opts['repl']=self.repl_s
            req_opts['incl']=self.incl_s
            req_opts['excl']=self.excl_s
            req_opts['fold']=self.fold_s
            req_opts['dept']-=1
            req_opts    = json.dumps(req_opts)
        report_to_tab(                      #NOTE: run-report
            rpt_data
           ,rpt_info
           ,how_rpt
           ,how_walk
           ,what_find
           ,what_save
           ,progressor  = progressor
           ,req_opts    = req_opts
           )
        progressor.set_progress(msg_rpt)
        ################################
        if 0<frgms and CLOSE_AFTER_GOOD:
            self.store()
            return None #break#while_fif

        return self.do_focus(aid,ag)
       #def do_work
       
    def get_fif_cnts(self, how=''): #NOTE: fif_cnts
        pass;                  #LOG and log('dlg_w, dlg_h={}',(dlg_w, dlg_h))
        pass;                  #LOG and log('gap1={}',(gap1))
        w_excl  = not self.wo_excl
        w_repl  = not self.wo_repl
        w_adva  = not self.wo_adva
        ad01    = 0             if self.wo_adva else 1
        c_more  = _('Mor&e >>') if self.wo_adva else _('L&ess <<')
        M       = FifD
        m       = self
        d       = dict
        if how=='vis+pos':  return [
 ('pres',d(          tid='incl'         ,w=38*3*ad01            ))
                                                                                                                   
,('rep_',d(          tid='repl'                     ,vis=w_repl ))
,('repl',d(          t  =5+    28+M.EG1             ,vis=w_repl ))
,('inc_',d(          tid='incl'                                 ))
,('incl',d(          t=m.gap1+ 56+M.EG2                         ))
,('exc_',d(          tid='excl'                     ,vis=w_excl )) 
,('excl',d(          t=m.gap1+ 84+M.EG3             ,vis=w_excl )) 
,('fol_',d(          tid='fold'                                 ))
,('fold',d(          t=m.gap2+112+M.EG4                         ))
,('brow',d(          tid='fold'                                 ))
,('dep_',d(          tid='dept'                                 ))
,('dept',d(          t=m.gap2+140+M.EG5                         ))
,('cfld',d(          tid='fold'                                 ))
,('----',d(          t=m.gap2+172+M.EG5                         ))
,('more',d(          t=m.gap2+160+M.EG5 ,cap=c_more             ))
,('arp_',d(          t=m.gap2+190+M.EG5             ,vis=w_adva ))
,('tot_',d(          tid='skip'                     ,vis=w_adva ))
,('totb',d(          tid='skip'                     ,vis=w_adva ))
,('join',d(          tid='sort'                     ,vis=w_adva ))
,('sht_',d(          tid='frst'                     ,vis=w_adva ))
,('shtp',d(          tid='frst'                     ,vis=w_adva ))
,('algn',d(          tid='enco'                     ,vis=w_adva ))
,('cntx',d(          tid='enco'                     ,vis=w_adva ))
                                                    
,('ase_',d(          t=m.gap2+190+M.EG5             ,vis=w_adva ))
,('ski_',d(          tid='skip'                     ,vis=w_adva ))
,('skip',d(          t=m.gap2+210+M.EG6             ,vis=w_adva ))
,('sor_',d(          tid='sort'                     ,vis=w_adva ))
,('sort',d(          t=m.gap2+237+M.EG7             ,vis=w_adva ))
,('frs_',d(          tid='frst'                     ,vis=w_adva ))
,('frst',d(          t=m.gap2+264+M.EG8             ,vis=w_adva ))
,('enc_',d(          tid='enco'                     ,vis=w_adva ))
,('enco',d(          t=m.gap2+291+M.EG9             ,vis=w_adva ))
                                                    
,('!rep',d(          tid='repl'                     ,vis=w_repl ))
,('!cnt',d(          tid='incl'                     ,vis=w_adva ))
,('cust',d(          t=m.gap2+264+M.EG8                         ))
,('help',d(          t=m.gap2+291+M.EG9                         ))
,('-'   ,d(          tid='dept'                               ))
  ] 
    # Start=Full cnts
        cnts    = [                                                                                                                                                       #  gmqz
 ('prs1',d(tp='bt'  ,t  =0              ,l=1000         ,w=0        ,sto=F  ,cap=_('&1')                                                            ,call=m.do_pres ))# &1
,('prs2',d(tp='bt'  ,t  =0              ,l=1000         ,w=0        ,sto=F  ,cap=_('&2')                                                            ,call=m.do_pres ))# &2
,('prs3',d(tp='bt'  ,t  =0              ,l=1000         ,w=0        ,sto=F  ,cap=_('&3')                                                            ,call=m.do_pres ))# &3
,('pres',d(tp='bt'  ,tid='incl'         ,l=5            ,w=38*3*ad01        ,cap=_('Pre&sets…')             ,hint=pset_h                            ,call=m.do_pres ))# &s
,('reex',d(tp='ch-b',tid='what'         ,l=5+38*0       ,w=38               ,cap='&.*'                      ,hint=reex_h            ,bind='reex01'  ,call=m.do_focus))# &.
,('case',d(tp='ch-b',tid='what'         ,l=5+38*1       ,w=38               ,cap='&aA'                      ,hint=case_h            ,bind='case01'  ,call=m.do_focus))# &a
,('word',d(tp='ch-b',tid='what'         ,l=5+38*2       ,w=38               ,cap='"&w"'                     ,hint=word_h            ,bind='word01'  ,call=m.do_focus))# &w
                                                                                                                                
,('wha_',d(tp='lb'  ,tid='what'         ,l=M.LBL_L      ,r=M.CMB_L-5        ,cap='>'+_('*&Find what:')                                                              ))# &f
,('what',d(tp='cb'  ,t  =5              ,l=M.CMB_L      ,w=M.TXT_W  ,a='lR' ,items=m.what_l                                         ,bind='what_s'                  ))# 
,('rep_',d(tp='lb'  ,tid='repl'         ,l=M.LBL_L      ,r=M.CMB_L-5        ,cap='>'+_('&Replace with:')                ,vis=w_repl                                 ))# &r
,('repl',d(tp='cb'  ,t  =5+    28+M.EG1 ,l=M.CMB_L      ,w=M.TXT_W  ,a='lR' ,items=m.repl_l                             ,vis=w_repl ,bind='repl_s'                  ))# 
,('inc_',d(tp='lb'  ,tid='incl'         ,l=M.LBL_L      ,r=M.CMB_L-5        ,cap='>'+_('*&In files:')       ,hint=mask_h                                            ))# &i
,('incl',d(tp='cb'  ,t=m.gap1+ 56+M.EG2 ,l=M.CMB_L      ,w=M.TXT_W  ,a='lR' ,items=m.incl_l                                         ,bind='incl_s'                  ))# 
,('exc_',d(tp='lb'  ,tid='excl'         ,l=M.LBL_L      ,r=M.CMB_L-5        ,cap='>'+_('Not in files:')     ,hint=mask_h,vis=w_excl                                 ))# 
,('excl',d(tp='cb'  ,t=m.gap1+ 84+M.EG3 ,l=M.CMB_L      ,w=M.TXT_W  ,a='lR' ,items=m.excl_l                             ,vis=w_excl ,bind='excl_s'                  ))# 
,('fol_',d(tp='lb'  ,tid='fold'         ,l=M.LBL_L      ,r=M.CMB_L-5        ,cap='>'+_('*I&n folder:')                                                              ))# &n
,('fold',d(tp='cb'  ,t=m.gap2+112+M.EG4 ,l=M.CMB_L      ,w=M.TXT_W  ,a='lR' ,items=m.fold_l                                         ,bind='fold_s'                  ))# 
,('brow',d(tp='bt'  ,tid='fold'         ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('&Browse…')              ,hint=brow_h                            ,call=m.do_fold ))# &b
,('dep_',d(tp='lb'  ,tid='dept'         ,l=M.LBL_L      ,w=100  -5          ,cap='>'+_('In s&ubfolders:')   ,hint=dept_h                                            ))# &u
,('dept',d(tp='cb-r',t=m.gap2+140+M.EG5 ,l=M.CMB_L      ,w=135              ,items=DEPT_L                                           ,bind='dept_n'                  ))# 
,('depa',d(tp='bt'  ,tid='dept'         ,l=1000         ,w=0        ,sto=F  ,cap=_('&l')                                                            ,call=m.do_dept ))# &l
,('depo',d(tp='bt'  ,tid='dept'         ,l=1000         ,w=0        ,sto=F  ,cap=_('&y')                                                            ,call=m.do_dept ))# &y
,('cfld',d(tp='bt'  ,tid='fold'         ,l=5            ,w=38*3             ,cap=_('&Current folder')       ,hint=cfld_h                            ,call=m.do_fold ))# &c
                                                                                                                                                     
,('----',d(tp='clr' ,t=m.gap2+172+M.EG5 ,l=0            ,w=1000 ,h=1        ,props=f('0,{},0,0',rgb_to_int(185,185,185))                                            ))#
,('more',d(tp='bt'  ,t=m.gap2+160+M.EG5 ,l=5            ,w=38*3             ,cap=c_more                     ,hint=more_h                            ,call=m.do_more ))# &e
                                                                                                                                                     
,('arp_',d(tp='lb'  ,t=m.gap2+190+M.EG5 ,l=5+80         ,r=M.CMB_L          ,cap=_('Adv. report options')               ,vis=w_adva                                 ))# 
,('tot_',d(tp='lb'  ,tid='skip'         ,l=5            ,r=80               ,cap='>'+_('Show in&:')                     ,vis=w_adva                                 ))# &:
,('totb',d(tp='cb-r',tid='skip'         ,l=5+80         ,r=M.CMB_L          ,items=m.totb_l                             ,vis=w_adva ,bind='totb_i'  ,call=m.do_totb ))# 
,('join',d(tp='ch'  ,tid='sort'         ,l=5+80         ,w=150              ,cap=_('Appen&d results')                   ,vis=w_adva ,bind='join_s'                  ))# &d
,('sht_',d(tp='lb'  ,tid='frst'         ,l=5            ,r=80               ,cap='>'+_('Tree type &/:')     ,hint=shtp_h,vis=w_adva                                 ))# &/
,('shtp',d(tp='cb-r',tid='frst'         ,l=5+80         ,r=M.CMB_L          ,items=SHTP_L                               ,vis=w_adva ,bind='shtp_s'                  ))# 
,('algn',d(tp='ch'  ,tid='enco'         ,l=5+80         ,w=100              ,cap=_('Align &|')              ,hint=algn_h,vis=w_adva ,bind='algn_s'                  ))# &|
,('cntx',d(tp='ch'  ,tid='enco'         ,l=5+170        ,w=150              ,cap=_('Conte&xt')              ,hint=cntx_h,vis=w_adva ,bind='cntx_s'  ,call=m.do_cntx ))# &x
                                                                                                                                                     
,('ase_',d(tp='lb'  ,t=m.gap2+190+M.EG5 ,l=M.TL2_L+100  ,r=M.TBN_L-GAP      ,cap=_('Adv. search options')               ,vis=w_adva                                 ))# 
,('ski_',d(tp='lb'  ,tid='skip'         ,l=M.TL2_L      ,w=100-5            ,cap='>'+_('S&kip files:')                  ,vis=w_adva                                 ))# &k
,('skip',d(tp='cb-r',t=m.gap2+210+M.EG6 ,l=M.TL2_L+100  ,r=M.TBN_L-GAP      ,items=SKIP_L                               ,vis=w_adva ,bind='skip_s'                  ))# 
,('sor_',d(tp='lb'  ,tid='sort'         ,l=M.TL2_L      ,w=100-5            ,cap='>'+_('S&ort file list:')              ,vis=w_adva                                 ))# &o
,('sort',d(tp='cb-r',t=m.gap2+237+M.EG7 ,l=M.TL2_L+100  ,r=M.TBN_L-GAP      ,items=SORT_L                               ,vis=w_adva ,bind='sort_s'                  ))# 
,('frs_',d(tp='lb'  ,tid='frst'         ,l=M.TL2_L      ,w=100-5            ,cap='>'+_('Firsts (&0=all):')  ,hint=frst_h,vis=w_adva                                 ))# &0
,('frst',d(tp='ed'  ,t=m.gap2+264+M.EG8 ,l=M.TL2_L+100  ,r=M.TBN_L-GAP                                                  ,vis=w_adva ,bind='frst_s'                  ))# 
,('enc_',d(tp='lb'  ,tid='enco'         ,l=M.TL2_L      ,w=100-5            ,cap='>'+_('Encodings &\\:')    ,hint=enco_h,vis=w_adva                                 ))# \
,('enco',d(tp='cb-r',t=m.gap2+291+M.EG9 ,l=M.TL2_L+100  ,r=M.TBN_L-GAP      ,items=ENCO_L                               ,vis=w_adva ,bind='enco_s'                  ))# 
                                                                                                                                                     
,('!fnd',d(tp='bt'  ,tid='what'         ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('Find'),def_bt=True      ,hint=find_h                            ,call=m.do_work ))# 
,('!rep',d(tp='bt'  ,tid='repl'         ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('Re&place')              ,hint=repl_h,vis=w_repl                 ,call=m.do_work ))# &p
,('!cnt',d(tp='bt'  ,tid='incl'         ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('Coun&t')                ,hint=coun_h,vis=w_adva                 ,call=m.do_work ))# &t
,('cust',d(tp='bt'  ,t=m.gap2+264+M.EG8 ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('Ad&just…')              ,hint=cust_h,sto=w_adva                 ,call=m.do_more ))# &j
,('loop',d(tp='bt'  ,tid='cust'         ,l=1000         ,w=0        ,sto=F  ,cap=_('&v')                                                            ,call=m.do_more ))# &v
,('help',d(tp='bt'  ,t=m.gap2+291+M.EG9 ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('&Help')                             ,sto=w_adva                 ,call=m.do_help ))# &h
,('-'   ,d(tp='bt'  ,tid='dept'         ,l=M.TBN_L      ,w=M.BTN_W  ,a='LR' ,cap=_('Close')                                                         ,call=m.do_exit ))# 
                ]
        self.caps   = {cid:cnt['cap']             for cid,cnt           in cnts
                        if cnt['tp'] in ('bt', 'ch')          and 'cap' in cnt}
        self.caps.update({cid:cnts[icnt-1][1]['cap'] for (icnt,(cid,cnt)) in enumerate(cnts)
                        if cnt['tp'] in ('cb', 'cb-r', 'ed')  and 'cap' in cnts[icnt-1][1]})
        self.caps   = {k:v.strip(' :*|\\/>*').replace('&', '') for (k,v) in self.caps.items()}
        return cnts
       #def get_cnts
    
    def get_fif_vals(self):
        vals    =       dict( reex=self.reex01
                             ,case=self.case01
                             ,word=self.word01
                             ,what=self.what_s
                             ,incl=self.incl_s
                             ,fold=self.fold_s
                             ,dept=self.dept_n
                            )
        if not self.wo_excl:
            vals.update(dict( excl=self.excl_s))
        if not self.wo_repl:
            vals.update(dict( repl=self.repl_s))
        if not self.wo_adva:
            vals.update(dict( join=self.join_s
                             ,totb=self.totb_i
                             ,shtp=self.shtp_s
                             ,cntx=self.cntx_s
                             ,algn=self.algn_s
                             ,skip=self.skip_s
                             ,sort=self.sort_s
                             ,frst=self.frst_s
                             ,enco=self.enco_s
                            ))
        pass;                  #LOG and log('vals={}',pf(vals))
        return vals
       #def get_fif_vals
    
   #class FifD

if __name__ == '__main__' :     # Tests
    Command().show_dlg()    #??
        
'''
ToDo
[+][kv-kv][25feb16] 'Sort files' with opts No/By date desc/By date asc 
[+][kv-kv][25feb16] 'First N files'
[+][kv-kv][25feb16] 'Append to results'
[-][kv-kv][25feb16] 'Show results in' with opts Panel/Tab/CB
[+][kv-kv][25feb16] 'Only count in each files'
[?][kv-kv][25feb16] 'Show files to select'
[+][kv-kv][25feb16] 'include/exclude masks'
[+][kv-kv][25feb16] 'depth' for recursion
[+][kv-kv][25feb16] 'preset'
[+][kv-kv][0?apr16] 'Firsts' for walk or for results?
[+][kv-kv][06apr16] testing re-expr correction on btn=='!...'
[+][kv-kv][06apr16] exclude file by size
[+][kv-kv][07apr16] how to show progress?
[+][kv-kv][08apr16] how to user can break?
[+][kv-kv][08apr16] 'try' to open next file
[+][kv-kv][08apr16] incl/excl many masks
[+][kv-kv][08apr16] if []==stores.get('incl')?
[+][kv-kv][08apr16] +Del/-Edit presets
[+][kv-kv][08apr16] status report: Found N fragments in M files
[+][kv-kv][14apr16] dont create new tab - reuse tab with max tag
[+][kv-kv][14apr16] opt: "compact output" (file:frag) or "lined" (file:\nfrag)
[+][a1-kv][15apr16] use ed selection for 'what'
[ ][kv-kv][15apr16] use next group for new tab
[+][kv-kv][15apr16] dont fill if 0 matches
[+][kv-kv][18apr16] wait ESC when fill tab
[?][kv-kv][18apr16] ? allow dir in What (like ST)
[?][kv-kv][19apr16] ? allow many roots
[+][kv-kv][20apr16] msg_st('', T) 
[+][kv-kv][20apr16] fold old res-reports before append new
[ ][kv-kv][21apr16] Show stage time in stat-data
[+][kv-kv][21apr16] Add %% to msg about stopping
[+][kv-kv][21apr16] Extra ops: lexers, wait 2nd+3rd ESC
[+][kv-kv][21apr16] Add plugin cmd "Find in cur file"
[+][kv-kv][22apr16] Transfer ops from local Find
[+][a1-kv][22apr16] Extra ops: Style for mark
[+][kv-kv][22apr16] Extra ops: Hide dlg after good res
[+][kv-kv][22apr16] Tips and ExtraOpts in dlg Help
[+][kv-kv][22apr16] Use text from Cud (not from disk!) for modifyed files
[ ][kv-kv][22apr16] Set caret to 1st fragment (with scroll)
[+][at-kv][26apr16] Move select_lexer,get_groups_count,html2rgb to cudax_lib
[+][kv-kv][26apr16] AsSubl: empty InFiles, InFolder ==> find in open files (ready preset?)
[+][kv-kv][26apr16] AsSubl: extra src lines as "context" in report
[+][kv-kv][29apr16] extra inf in title: 10 must be opts
[?][kv-kv][29apr16] aligning for MIDDL need in each dir 
[ ][kv-kv][29apr16] ! find_in_ed must pass to dlg title + tab_id
[+][kv-kv][29apr16] extract 'pres' to dlg_preset
[-][kv-kv][04may16] BUG? Encoding ex breaks reading file ==> next encoding doubles stat data
[+][a1-kv][10may16] Replace in files
[+][at-kv][10may16] Checks for preset
[+][kv-kv][11may16] Try to save last active control
[+][kv-kv][13may16] Set empty Exclude if hidden
[?][kv-kv][13may16] Custom: hide Append+Firsts
[?][kv-kv][13may16] UnDo for ReplaceInFiles by report
[-][kv-kv][13may16] Auto-Click-More before focus hidden field
[+][kv-kv][13may16] Ask "Want repl in OPEN TABS"
[+][kv-kv][13may16] Use os.access(path, os.W_OK)
[+][kv-kv][14may16] Calc place for new fragment: old_head|new|old_tail
[+][a1-kv][14may16] Mark new fragments with new styles
[ ][at-kv][14may16] Optim rpt filling
[+][kv-kv][25may16] Save fold after Browse
[+][kv-kv][30may16] Add tree type path/(r):line
[+][a1-kv][31may16] Use source EOL to save after replacements
[+][kv-kv][01jun16] Use Ctrl/Shift/Alt for more action
[+][kv-kv][02jun16] Add buttons "#&1", "#&2", "#&3" for direct load Preset #1, #2, #3 (outside? width=0!)
[+][kv-kv][11jun16] Add "/folder-mask" for incl/excl
[ ][kv-kv][11jun16] ? Lazy/Yield for cllc--find--rept ?
[-][kv-kv][14jun16] Opt "save active tab on Close" ?
[+][kv-kv][14jun16] Cmds "Show next/prev result" ?
[+][kv-kv][09feb17] Set dept="folder only" when cmd "Search in cur file"
[+][kv-kv][09feb17] Clear excl when cmd "Search in cur file"
[+][kv-kv][09feb17] Clear excl when cmd "Search in cur tab"
[ ][kv-kv][09feb17] ? New menu cmd (wo dlg): Find sel in cur file
[ ][kv-kv][09feb17] ? New menu cmd (wo dlg): Find sel in cur tab
[ ][kv-kv][09feb17] ? New menu cmd (wo dlg): Find sel in all tab
[ ][kv-kv][09feb17] ? New menu cmd (wo dlg): Find sel in cur dir
[+][kv-kv][09feb17] Help: show button "open user.json" when Opt, ref "RE" when Tips
[+][kv-kv][09feb17] Replace "..." to "…"
[ ][kv-kv][09feb17] After stoping show (2942 matches in 166 (stop at NN%) files)
[+][at-kv][00feb17] DblClick to nav
[ ][kv-kv][15feb17] More scam-Find command: Close dlg, Nav to first result
[+][kv-kv][22feb17] Opt to "Show in" fixed fif-file(s)
[+][kv-kv][23feb17] scam+Less/More to hide/show excl or repl
[+][kv-kv][23feb17] "In subf" v-align with "In fold"
[-][kv-kv][23feb17] Show min width in Cust
[+][kv-kv][23feb17] Show "Show in"+"Append"+"Tree type" in title for compact mode
[+][at-kv][22mat17] "fif_read_head_size(bytes)"
[+][kv-kv][23mat17] "fif_context_width_before", "fif_context_width_after"
[ ][kv-kv][30mat17] Sort and Tree conflict is too hard. Use "Stop? Without sort?"
[+][kv-kv][30mat17] !! Need Properties dlg to show/edit opts from/to user.json
[-][kv-kv][12apr17] os.walk is wide or depth? How to switch mode?
[ ][kv-kv][17apr17] ? Use local menu to show presets (after dlg_proc)
[+][kv-kv][28apr17] ReStore user's (x,y) for dlg (after dlg_proc)
[+][kv-kv][03may17] BUG on move in ConfigPreset
[+][kv-kv][03may17] Hide Collect in ConfigPreset and SavePreset
[+][kv-kv][12may17] Use T/F as short form of True/False
[+][kv-kv][15may17] Help and Adjust to move to right+bottom, Close not to relocate, DlgHeight to reduce
[ ][at-kv][19may17] Anchor --- to right
[ ][at-kv][31may17] Live apply changes from opt-dlg
[ ][at-kv][31may17] en=F for PresDlg Up/Dn if sel=0/max
[ ][at-kv][31may17] ? Use pages control for Help
[ ][kv-kv][01jun17] ? Show in Help ref to Issues on GH
[ ][kv-kv][01jun17] ? Add hidden button to find in current file (=Shift+"CurrFold")
[ ][kv-kv][16jun17] Show src ed AFTER set src caret to fragment
'''
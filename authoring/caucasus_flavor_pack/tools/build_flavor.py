#!/usr/bin/env python3
"""Build the authored English flavor scripts from explicit content records."""
from pathlib import Path
import json
from ck3_script import write
ROOT=Path(__file__).resolve().parents[1]
L={}
def loc(k,v):L[k]=v

def decision(key,title,desc,county,effect,cost=100,cooldown=5,valid='',shown='',tooltip=''):
 loc(key,title);loc(key+'_desc',desc);loc(key+'_tooltip',tooltip or 'Invest in this county and hear the proposals of its residents.');loc(key+'_confirm','Make the arrangements')
 picture='CAUC_derbent_pass' if county=='c_derbent' else 'decision_castle_view'
 return f'''{key} = {{
 picture = {{ reference = "gfx/interface/illustrations/decisions/{picture}.dds" }}
 decision_group_type = RICE_regional
 desc = {key}_desc
 selection_tooltip = {key}_tooltip
 confirm_text = {key}_confirm
 ai_check_interval_by_tier = {{ barony = 0 county = 48 duchy = 48 kingdom = 64 empire = 64 hegemony = 64 }}
 cooldown = {{ years = {cooldown} }}
 is_shown = {{ is_landed = yes has_title = title:{county} {shown} }}
 is_valid = {{ {valid} }}
 is_valid_showing_failures_only = {{ is_available_adult = yes is_imprisoned = no is_at_war = no }}
 effect = {{ {effect} }}
 cost = {{ gold = {cost} }}
 ai_potential = {{ short_term_gold >= {cost*2} }}
 ai_will_do = {{ base = 20 }}
}}'''

def event(number,title,desc,county,condition,options,theme='stewardship',triggered=True):
 key='CAUC.'+number
 loc(key+'.t',title);loc(key+'.desc',desc)
 s=f'{key} = {{\n type = character_event\n title = {key}.t\n desc = {key}.desc\n theme = {theme}\n left_portrait = {{ character = root }}\n trigger = {{ is_landed = yes is_available_adult = yes is_imprisoned = no has_title = title:{county} {condition} }}\n'
 for i,(name,effect,trigger) in enumerate(options):
  suffix=chr(ord('a')+i);loc(key+'.'+suffix,name)
  s+=f' option = {{ name = {key}.{suffix} '
  if trigger:s+='trigger = { '+trigger+' } '
  s+=effect+' ai_chance = { base = 50 } }\n'
 s+='}\n';return s

def cm(county,name,years):return f'title:{county} = {{ add_county_modifier = {{ modifier = {name} years = {years} }} }}'
def control(county,n):return f'title:{county} = {{ change_county_control = {n} }}'
def removed(county,name):return f'title:{county} = {{ remove_county_modifier = {name} }}'
def has(county,name):return f'title:{county} = {{ has_county_modifier = {name} }}'

def main():
 decisions=[];events=[]
 policies=['CAUC_pass_trade','CAUC_pass_guard','CAUC_pass_compact']
 policy_clear=' '.join(removed('c_derbent',p) for p in policies)
 options=[]
 for p,title,body in [('CAUC_pass_trade','Set aside space for merchants.','Local merchants receive support for their work.'),('CAUC_pass_guard','Provide stores for the garrison.','The garrison receives provisions and repairs.'),('CAUC_pass_compact','Agree on duties with the nearby settlements.','Residents gain a defined share of maintenance obligations.')]:
  options.append((title,policy_clear+' '+cm('c_derbent',p,5),''))
 events.append(event('0001','The Gate of $c_derbent$','My overseer lays out the accounts for the repaired road and walls. Merchants want more room for their caravans. The garrison asks for stores, while the nearby settlements want me to settle their obligations. I have enough funds to support one proposal for the coming years.','c_derbent',has('c_derbent','CAUC_pass_restored'),options))
 decisions.append(decision('CAUC_repair_derbent_pass','Repair the Passage at $c_derbent$','The walls and approaches at $c_derbent$ need repair. I can pay local workers to restore the route and decide how to support the people who maintain it.','c_derbent',cm('c_derbent','CAUC_pass_restored',10)+' trigger_event = { id = CAUC.0001 }',100,5,'NOT = { '+has('c_derbent','CAUC_pass_restored')+' }',tooltip='Repair the passage for ten years, then choose a five-year policy. The policy belongs to the county and survives a change of ruler.'))
 decisions.append(decision('CAUC_manage_derbent_pass','Review the Passage at $c_derbent$','The passage needs a policy suited to its current circumstances. I will summon those responsible for the road, the garrison and the nearby settlements to review our arrangements.','c_derbent','trigger_event = { id = CAUC.0001 }',25,3,has('c_derbent','CAUC_pass_restored'),has('c_derbent','CAUC_pass_restored'),tooltip='Replace the current passage policy with a new five-year arrangement.'))
 christian='faith = { religion = religion:christianity_religion }'
 decisions.append(decision('CAUC_patronize_lori_learning','Support the Scholars of $c_lori$','The monastic communities of $c_lori$ need patrons for teaching, copying books and maintaining their buildings. I can offer a grant while leaving the scholars to organize their work.','c_lori',cm('c_lori','CAUC_lori_learning',5)+' trigger_event = { id = CAUC.0002 }',100,5,'NOT = { '+has('c_lori','CAUC_lori_learning')+' }',christian,tooltip='Fund local learning for five years and choose the purpose of your grant. This supports local institutions without inventing a named monastery before its foundation.'))
 events.append(event('0002','A Grant for the Scholars','The monks bring a list of their needs: parchment for copying, support for pupils and repairs to rooms where they work. My grant will cover one undertaking. They ask me to name my preference before they commit the funds.','c_lori',has('c_lori','CAUC_lori_learning'),[('Provide materials for the copyists.','add_piety = 100',''),('Pay for the pupils to study.','add_learning_lifestyle_xp = 150',''),('Repair the rooms before the next winter.',control('c_lori',5),'')],theme='learning'))
 decisions.append(decision('CAUC_support_svan_towers','Support the Tower Communities of $c_svaneti$','Families in $c_svaneti$ maintain towers that shelter their households and provide places of defense. I can help them repair the masonry and agree on the work they will undertake.','c_svaneti',cm('c_svaneti','CAUC_svan_towers',5)+' trigger_event = { id = CAUC.0003 }',100,5,'NOT = { '+has('c_svaneti','CAUC_svan_towers')+' }',tooltip='Support local tower repairs for five years and settle how the communities will contribute.'))
 events.append(event('0003','The Work on the Towers','The households have sent representatives to discuss repairs. Some can supply labor; others would rather provide grain or stone. My steward wants one rule for everyone, but the representatives ask me to account for what each household can spare.','c_svaneti',has('c_svaneti','CAUC_svan_towers'),[('Accept contributions in labor and supplies.',control('c_svaneti',5),''),('Pay skilled masons from my own funds.','add_gold = -25 '+cm('c_svaneti','CAUC_svan_masons',3),'gold >= 25'),('Let the communities apportion the work.','add_prestige = 75','')],theme='diplomacy'))
 decisions.append(decision('CAUC_support_gelati','Endow Learning near $b_kutaisi$','I can support teachers and copyists near $b_kutaisi$, where a ruler may cultivate a lasting center of learning. The grant concerns the work of scholars; it does not assume that my dynasty built the historical monastery of Gelati.','c_odishi',cm('c_odishi','CAUC_gelati_learning',5)+' trigger_event = { id = CAUC.0004 }',150,5,'current_date >= 1106.1.1 NOT = { '+has('c_odishi','CAUC_gelati_learning')+' }',christian+' current_date >= 1106.1.1',tooltip='Support local learning for five years. Available from 1106, the historical beginning of construction at Gelati.'))
 events.append(event('0004','Teachers near $b_kutaisi$','The teachers ask for funds to acquire books and keep their pupils at study. A copyist has also proposed a volume bearing my name as patron. I must decide how much of the grant should serve my reputation.','c_odishi',has('c_odishi','CAUC_gelati_learning'),[('Let the teachers choose the books.','add_learning_lifestyle_xp = 200',''),('Remember my house in the dedication.','add_prestige = 100','')],theme='learning'))
 # Six independently gated passage events.
 passage=has('c_derbent','CAUC_pass_restored')+' is_at_war = no'
 E=[
 ('0010','The Repair Accounts','My overseer has found damage to a retaining wall beside the approach to $c_derbent$. The workers can repair it now, but they need another payment. Delaying the work would spare my treasury and leave the nearby households to cope with the damage.',[('Pay for the repair.','add_gold = -25 '+control('c_derbent',2),'gold >= 25'),('Ask the households to manage until next year.',control('c_derbent',-3),'')],passage),
 ('0011','Space for a Caravan','A caravan has reached $c_derbent$, and its merchants complain that the space allotted to their animals is too cramped. They offer to pay for more room. My steward warns that granting their request will inconvenience the residents who use the same ground.',[('Grant the space for a fee.','add_gold = 20 '+control('c_derbent',-2),''),('Keep the residents\' access clear.','add_prestige = 25','')],passage+' '+has('c_derbent','CAUC_pass_trade')),
 ('0012','Stores for the Watch','The officer responsible for the passage shows me the remaining stores. There is enough for the current watch, but little to cover a longer posting. I can purchase supplies or shorten the men\'s duties.',[('Buy the stores.','add_gold = -20 '+control('c_derbent',3),'gold >= 20'),('Shorten this posting.',control('c_derbent',-2),'')],passage+' '+has('c_derbent','CAUC_pass_guard')),
 ('0013','A Dispute over Road Work','Two settlements disagree over the maintenance of a stretch of road near $c_derbent$. Each claims that the other benefited more from last year\'s repairs. Their representatives have brought me their accounts and ask me to settle the division of work.',[('Hear their accounts and divide the duties.','add_stress = 10 '+control('c_derbent',3),''),('Pay workers to finish the disputed stretch.','add_gold = -20','gold >= 20')],passage+' '+has('c_derbent','CAUC_pass_compact')),
 ('0014','Visitors at the Gate','My officials report a small party of visitors seeking passage through $c_derbent$. They carry letters of introduction and ask for help finding an escort. I can meet their needs through my household or leave them to make arrangements in the town.',[('Have my household receive them.','add_gold = -15 add_prestige = 40','gold >= 15'),('The town can provide what they need.','add_gold = 5','')],passage),
 ('0015','Stone on the Approach','Falling stone has obstructed part of the approach to $c_derbent$. Travelers can pass, but carts must wait while laborers clear a track. The overseer wants funds to complete the work before the next caravan arrives.',[('Hire the extra workers.','add_gold = -40','gold >= 40'),('Clear it with the labor already available.',cm('c_derbent','CAUC_pass_obstructed',2),'')],passage),
 ]
 for number,title,desc,options,condition in E:events.append(event(number,title,desc,'c_derbent',condition,options))
 # Six learning events, available only to the current patron of Lori.
 school=has('c_lori','CAUC_lori_learning')+' '+christian+' is_at_war = no'
 S=[
 ('0020','The Cost of Parchment','The copyists in $c_lori$ have used more parchment than their grant allowed. They ask me to pay for another supply or permit them to postpone part of their work.',[('Pay for the parchment.','add_gold = -20 add_piety = 40','gold >= 20'),('Finish the books already begun.','add_learning_lifestyle_xp = 50','')]),
 ('0021','A Place for a Pupil','A teacher in $c_lori$ writes on behalf of a pupil whose household cannot afford further study. The teacher considers the pupil able and asks me to cover the cost.',[('Support the pupil.','add_gold = -25 add_learning_lifestyle_xp = 100','gold >= 25'),('Ask the institution to use its existing grant.','add_piety = 20','')]),
 ('0022','A Difficult Passage','A scholar from $c_lori$ has sent me two readings of a passage in a theological work. The copyists disagree over which reading belongs in their new volume. The scholar invites me to hear the evidence.',[('Make time for the discussion.','add_stress = 10 add_learning_lifestyle_xp = 100',''),('Leave the question to the scholars.','add_piety = 25','')]),
 ('0023','The Patron\'s Name','A copyist offers to name my house in the dedication of a new book. The other patrons have already paid for much of the work. I can claim the place of honor or ask the copyist to record their contributions alongside mine.',[('Record the other patrons as well.','add_piety = 40',''),('My house should receive the place of honor.','add_prestige = 40','')]),
 ('0024','Rain in the Workroom','A damaged roof has let rain into a workroom in $c_lori$. The scholars have moved the books, but they need help repairing the room before they can resume copying there.',[('Fund the repairs.','add_gold = -30 add_piety = 40','gold >= 30'),('Use another room for the remaining work.',control('c_lori',-2),'')]),
 ('0025','A Book at My Table','A scholar brings a completed volume from $c_lori$ and offers to explain it at my table. My attendants have other business waiting. I can postpone it and spend the afternoon reading.',[('Read with the scholar.','add_stress = 10 add_learning_lifestyle_xp = 125',''),('Thank the scholar and display the volume.','add_prestige = 40','')]),
 ]
 for number,title,desc,options in S:events.append(event(number,title,desc,'c_lori',school,options,theme='learning'))
 # Six community events, tied to the current county holder rather than ethnicity.
 tower=has('c_svaneti','CAUC_svan_towers')+' is_at_war = no'
 T=[
 ('0030','A Turn at the Work','Representatives from $c_svaneti$ disagree over which households should provide workers for the next repairs. One household has supplied labor twice; another argues that it contributed stone in place of workers.',[('Review the contributions before assigning duties.','add_stress = 10 '+control('c_svaneti',3),''),('Pay workers to settle this round.','add_gold = -20','gold >= 20')]),
 ('0031','A Mason\'s Proposal','A mason in $c_svaneti$ has proposed repairs to a tower\'s upper floor. The household can supply materials, but it asks me to pay for the mason\'s work.',[('Pay the mason.','add_gold = -25 '+cm('c_svaneti','CAUC_svan_masons',2),'gold >= 25'),('Have the household undertake a smaller repair.','add_prestige = 20','')]),
 ('0032','Work before the Harvest','The overseer in $c_svaneti$ wants to summon workers for repairs. Several households ask him to wait until they have brought in their harvest. I must choose between finishing the work and leaving them time in their fields.',[('Wait for the harvest.',control('c_svaneti',2),''),('Hire workers who can begin now.','add_gold = -20 '+cm('c_svaneti','CAUC_svan_masons',2),'gold >= 20')]),
 ('0033','The Community Accounts','The representatives of $c_svaneti$ have gathered to compare their contributions to the repairs. They invite me to hear the accounts and confirm the duties they propose for the coming year.',[('Hear the accounts in person.','add_stress = 10 '+control('c_svaneti',4),''),('Send funds with my steward.','add_gold = -15 add_prestige = 25','gold >= 15')]),
 ('0034','Shelter for Travelers','Travelers have asked a household in $c_svaneti$ for shelter while they wait for better weather. The household has little to spare and requests provisions from my stores.',[('Send them provisions.','add_gold = -15 add_prestige = 40','gold >= 15'),('Ask several households to share the burden.',control('c_svaneti',-2),'')]),
 ('0035','The Watch near the Towers','The men keeping watch near the towers in $c_svaneti$ ask for repairs to their shelter and a supply of grain. Their spokesman presents the request as part of the maintenance I promised to support.',[('Honor the undertaking.','add_gold = -25 '+control('c_svaneti',3),'gold >= 25'),('Keep this year\'s spending within the grant.','add_prestige = 15','')]),
 ]
 for number,title,desc,options in T:events.append(event(number,title,desc,'c_svaneti',tower,options,theme='diplomacy'))
 write(ROOT/'common/decisions/CAUC_regional_decisions.txt','\n\n'.join(decisions))
 write(ROOT/'events/CAUC_regional_events.txt','namespace = CAUC\n\n'+'\n\n'.join(events))
 mods={
 'CAUC_pass_restored':('Repaired Passage','Local workers have repaired the walls and approaches of the passage.','development_growth_factor = 0.05'),
 'CAUC_pass_trade':('Support for Caravans','The county supports merchants and provides space for their caravans.','tax_mult = 0.05'),
 'CAUC_pass_guard':('Provisions for the Watch','The local ruler has set aside supplies for the garrison.','fort_level = 0.25'),
 'CAUC_pass_compact':('Agreed Maintenance Duties','Settlements share defined obligations for maintaining the passage.','monthly_county_control_growth_add = 0.1'),
 'CAUC_pass_obstructed':('Obstructed Approach','Laborers are clearing fallen stone from the approach.','tax_mult = -0.05'),
 'CAUC_lori_learning':('Patronage of Local Scholars','A patron supports teaching and copying in the monastic communities of Lori.','development_growth_factor = 0.05'),
 'CAUC_svan_towers':('Supported Tower Repairs','Households receive support for maintaining their tower dwellings.','fort_level = 0.25'),
 'CAUC_svan_masons':('Work of Skilled Masons','Skilled masons have undertaken repairs to local towers.','fort_level = 0.25'),
 'CAUC_gelati_learning':('Learning near Kutaisi','A patron supports teachers and copyists near Kutaisi.','development_growth_factor = 0.05'),
 }
 for k,(name,desc,_) in mods.items():loc(k,name);loc(k+'_desc',desc)
 write(ROOT/'common/modifiers/CAUC_regional_modifiers.txt','\n\n'.join(k+' = {\n '+body+'\n}' for k,(_,_,body) in mods.items()))
 pulse='''on_game_start_after_lobby = { on_actions = { CAUC_setup_on_action } }
CAUC_setup_on_action = {
 effect = {
  if = {
   limit = { NOT = { has_global_variable = CAUC_initialized } }
   set_global_variable = { name = CAUC_initialized value = yes }
   if = {
    limit = { has_game_rule = CAUC_ce_setup_on CAUC_ce_present_trigger = no }
    if = { limit = { game_start_date = 867.1.1 } CAUC_CE_setup_867_effect = yes }
    else_if = { limit = { game_start_date = 1066.9.15 } CAUC_CE_setup_1066_effect = yes }
    else_if = { limit = { game_start_date = 1178.10.1 } CAUC_CE_setup_1178_effect = yes }
   }
  }
 }
}
yearly_playable_pulse = { on_actions = { CAUC_regional_yearly_pulse } }
CAUC_regional_yearly_pulse = {
 trigger = {
  is_landed = yes is_available_adult = yes is_imprisoned = no is_at_war = no
  OR = { has_title = title:c_derbent has_title = title:c_lori has_title = title:c_svaneti }
 }
 random_events = {
  chance_to_happen = 30
'''
 for n in [x[0] for x in E+S+T]:pulse+='  10 = CAUC.'+n+'\n'
 pulse+=' }\n}\n'
 write(ROOT/'common/on_action/CAUC_on_actions.txt',pulse)
 write(ROOT/'common/scripted_triggers/CAUC_compatibility_triggers.txt','CAUC_ce_present_trigger = { always = no }')
 write(ROOT/'common/game_rules/CAUC_game_rules.txt','''CAUC_ce_setup = {
 categories = { RICE setup flavor }
 default = CAUC_ce_setup_on
 CAUC_ce_setup_on = { }
 CAUC_ce_setup_off = { }
}''')
 for k,v in {'rule_CAUC_ce_setup':'Caucasus: Culture Expanded Setup','setting_CAUC_ce_setup_on':'Use Regional CE Setup','setting_CAUC_ce_setup_on_desc':'Apply the Caucasus culture distribution, innovation inheritance and historical character culture corrections from Culture Expanded at the supported start dates. CE\'s own setup takes precedence when the CE compatibility overlay is loaded.','setting_CAUC_ce_setup_off':'Keep the Starting Distribution','setting_CAUC_ce_setup_off_desc':'Keep the base mod\'s starting county and character cultures. Imported cultures remain available.','CAUC_establish_transcaucasia_trigger':'Establish Transcaucasia through the decision before creating this title.'}.items():loc(k,v)
 # RICE-style optional historical background. Keep development details out of
 # the player's decision flow.
 contexts = {
  'CAUC_repair_derbent_pass': 'Fortifications at Derbent guarded the narrow passage between the Caucasus and the Caspian Sea. Successive rulers maintained the walls and governed the town between them.',
  'CAUC_patronize_lori_learning': 'Haghpat and Sanahin developed as centers of learning in medieval Armenia. Their patrons supported architecture, manuscript production and teaching.',
  'CAUC_support_svan_towers': 'Tower houses in Upper Svaneti served households as dwellings and places of defense. Repairs required materials, skilled work and contributions from residents.',
  'CAUC_support_gelati': 'David IV began building Gelati near Kutaisi in 1106. Scholars at its academy taught, translated texts and copied manuscripts.'
 }
 p=ROOT/'common/decisions/CAUC_regional_decisions.txt'
 text=p.read_text(encoding='utf-8-sig')
 for key,context in contexts.items():
  loc(key+'_context',context)
  start=text.index(key+' = {');effect=text.index('effect = {',start)+len('effect = {')
  text=text[:effect]+' if = { limit = { has_game_rule = RICE_historical_context_on } custom_tooltip = '+key+'_context } '+text[effect:]
 write(p,text)
 loc('CAUC_patronize_lori_learning_tooltip','Fund local teaching and copying for five years, then choose the purpose of your grant.')
 loc('CAUC_support_gelati_desc',"Teachers and copyists near $b_kutaisi$ seek a patron. I can provide books and funds for their pupils, or commission a volume that records my house's support.")
 loc('CAUC_support_gelati_tooltip','Fund local learning for five years and choose how the scholars use your grant.')
 # Make the copied empire effect match its decision tooltip: account for the new
 # duchy title and perform de-jure changes only when a player forms the empire.
 p=ROOT/'common/scripted_effects/CAUC_CE_flavor_effects.txt';s=p.read_text(encoding='utf-8-sig')
 if 'title:d_shirvan = { set_de_jure_liege_title = title:k_shirvan }' not in s:
  s=s.replace('create_title_and_vassal_change = {','title:d_shirvan = { set_de_jure_liege_title = title:k_shirvan }\n title:k_georgia = { set_de_jure_liege_title = title:e_CAUC_transcaucasia }\n title:k_armenia = { set_de_jure_liege_title = title:e_CAUC_transcaucasia }\n title:k_shirvan = { set_de_jure_liege_title = title:e_CAUC_transcaucasia }\n create_title_and_vassal_change = {',1)
 write(p,s)
 text='l_english:\n'+'\n'.join(' '+k+':0 "'+v.replace('"','\\"').replace('\n','\\n')+'"' for k,v in sorted(L.items()))
 write(ROOT/'localization/english/CAUC_flavor_l_english.yml',text)
 (ROOT/'research/authored-content.json').write_text(json.dumps({'version':'0.1.0','language':'english','decisions':len(decisions),'visible_events':len(events),'yearly_events':len(E+S+T),'gameplay_localization_keys':len(L),'naming':'Vanilla c_derbent/b_derbent aliases; Chinese must use 杰尔宾特.','historical_context_sources':['https://whc.unesco.org/en/list/1070','https://whc.unesco.org/en/list/777/','https://whc.unesco.org/en/list/709','https://whc.unesco.org/en/list/710'],'note':'Event scenes and outcomes are authored gameplay fiction grounded in the selected topics; specific household disputes, conversations and accounts are not presented as documented historical incidents.'},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'decisions':len(decisions),'events':len(events),'yearly_events':len(E+S+T),'english_keys':len(L)}))
if __name__=='__main__':main()

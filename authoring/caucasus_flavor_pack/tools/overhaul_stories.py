"""Character-led stories, persistent choices, native recruitment and a dated outbreak."""
from pathlib import Path
from ck3_script import entries, write
ROOT=Path(__file__).resolve().parents[1]
LANGS=('english','simp_chinese','french')

def replace_field(raw,key,value):
 start=raw.index('{')+1;body=raw[start:raw.rfind('}')]
 for k,v,a,z in entries(body):
  if k==key:return raw[:start]+body[:a]+key+' = { '+value+' }'+body[z:]+'}'
 return raw[:raw.rfind('}')]+key+' = { '+value+' }\n}'

def cast_effect(role,culture,faith,traits,skills,age=40,female=0):
 return f'''CAUC_{role}_speaker_effect = {{
 if = {{ limit = {{ has_variable = CAUC_{role}_speaker var:CAUC_{role}_speaker = {{ is_alive = yes }} }}
  var:CAUC_{role}_speaker = {{ save_scope_as = CAUC_{role}_speaker }}
 }} else = {{
  create_character = {{ age = {age} dynasty = none gender_female_chance = {female} random_traits = no
   location = root.capital_province culture = {culture} faith = {faith}
   {' '.join('trait = '+x for x in traits.split())} {skills} save_scope_as = CAUC_{role}_speaker
  }}
  add_visiting_courtier = scope:CAUC_{role}_speaker
  set_variable = {{ name = CAUC_{role}_speaker value = scope:CAUC_{role}_speaker }}
 }}
}}\n'''

def overhaul(events,decisions,modifiers,flows,loc):
 def L(key,en,zh,fr):
  for lang,value in zip(LANGS,(en,zh,fr)):loc[lang][key]=value
 def opinion(who,n):return 'scope:CAUC_'+who+'_speaker = { add_opinion = { modifier = friendliness_opinion target = root opinion = '+str(n)+' years = 10 } }'
 def recruit(who):return 'add_courtier = scope:CAUC_'+who+'_speaker'
 def nxt(n,days=45):return f'trigger_event = {{ id = CAUC.{n:04d} days = {days} }}'
 def chosen(county,flow,n):return f'title:{county} = {{ set_variable = {{ name = CAUC_{flow}'+('' if flow.endswith('_use') else '_choice')+f' value = {n} }} }}'
 def final_policy(county,flow,n,names):
  return 'title:'+county+' = { '+' '.join('remove_county_modifier = '+x for x in names)+' add_county_modifier = { modifier = '+names[n-1]+' years = 5 } } '+chosen(county,flow,n)
 def end(flow):
  roles={'derbent_guards':['rus'],'lori_council':['abbot','envoy'],'ani_sanctuary':['warden','imam'],'alan_mission':['missionary','elder']}.get(flow,[])
  cleanup=' '.join('if = { limit = { scope:CAUC_'+r+'_speaker = { NOT = { is_courtier_of = root } } } remove_courtier_or_guest = scope:CAUC_'+r+'_speaker }' for r in roles)
  return 'remove_character_flag = CAUC_'+flow+'_active '+cleanup
 def army():return 'spawn_army = { name = CAUC_rus_event_army levies = 500 location = root.capital_province inheritable = no war_keep_on_attacker_victory = yes }'
 def book(key,creator):return 'create_artifact = { name = '+key+' description = '+key+'_desc type = book visuals = book template = general_unique_template wealth = 25 quality = 25 modifier = CAUC_scholarly_book_modifier creator = scope:CAUC_'+creator+'_speaker }'
 def scene(n,county,role,desc,options,extra='',theme='diplomacy',immediate=''):
  key=f'CAUC.{n:04d}';L(key+'.desc',*desc)
  body=f'''{key} = {{ type = character_event title = {key}.t desc = {key}.desc theme = {theme}
 left_portrait = {{ character = root }} right_portrait = {{ character = scope:CAUC_{role}_speaker }}
 trigger = {{ is_landed = yes is_available_adult = yes is_imprisoned = no has_title = title:{county} {extra} }}
 immediate = {{ CAUC_{role}_speaker_effect = yes {immediate} }}\n'''
  for i,(words,effect,gate) in enumerate(options):
   name=key+'.'+chr(97+i);L(name,*words)
   body+=' option = { name = '+name+(' trigger = { '+gate+' }' if gate else '')+' '+effect+' ai_chance = { base = 50 } }\n'
  return body+'}\n'
 C='faith = { religion = religion:christianity_religion }';M='faith = { religion = religion:islam_religion }'
 effects='''# Cast is stored on the ruler and recovered at every delayed stage, including after reload.\n'''
 effects+=cast_effect('rus','culture:russian','faith:slavic_pagan','education_martial_4 brave gallant lifestyle_blademaster','martial = 26 prowess = 32 diplomacy = 12 learning = 8',age=30)
 # 1 + min(32*4,50) + brave 20 + blademaster 15 + gallant 5 = 91;
 # even the native palace-politics -10 leaves 81, above Excellent's 80.
 effects=effects.replace('set_variable = { name = CAUC_rus_speaker', 'scope:CAUC_rus_speaker = { add_trait_xp = { trait = lifestyle_blademaster value = 100 } }\n  set_variable = { name = CAUC_rus_speaker')
 for role,culture,faith,traits,skills in [
 ('abbot','culture:armenian','faith:armenian_apostolic','education_learning_4 theologian zealous humble','learning = 24 diplomacy = 13'),
 ('envoy','culture:greek','faith:orthodox','education_learning_4 scholar patient','learning = 22 diplomacy = 16'),
 ('warden','culture:armenian','faith:armenian_apostolic','education_learning_3 diligent humble','learning = 17 stewardship = 15'),
 ('imam','culture:armenian','faith:sunni','education_learning_3 zealous patient','learning = 18 diplomacy = 14'),
 ('missionary','culture:greek','faith:orthodox','education_learning_4 theologian zealous','learning = 23 diplomacy = 14'),
 ('elder','culture:alan','root.faith','education_diplomacy_3 stubborn brave','diplomacy = 18 martial = 16 prowess = 20'),
 ('representative','culture:armenian','faith:armenian_apostolic','education_learning_3 brave compassionate','learning = 17 diplomacy = 17')]:
  effects+=cast_effect(role,culture,faith,traits,skills, female=100 if role=='representative' else 0)
 effects+='CAUC_tondrakian_speaker_effect = { CAUC_tondrakian_recover_speaker_effect = yes }\n'
 # The representative is explicitly a member of the new rite, not a generic outsider.
 effects+='CAUC_tondrakian_witness_effect = { CAUC_representative_speaker_effect = yes scope:CAUC_representative_speaker = { set_character_rite = rite:CAUC_tondrakian_rite } }\n'
 effects+=cast_effect('overseer','root.culture','root.faith','education_stewardship_3 diligent','stewardship = 20 martial = 14')
 effects+=cast_effect('scholar','root.culture','root.faith','education_learning_4 scholar patient','learning = 24 diplomacy = 13')
 effects+=cast_effect('mason','culture:ce_svan','root.faith','education_stewardship_3 diligent brave','stewardship = 21 prowess = 16 martial = 14',age=35)
 write(ROOT/'common/scripted_effects/CAUC_story_cast_effects.txt',effects)
 L('CAUC_rus_event_army','Rus Company','罗斯战团','Compagnie rus’')
 L('CAUC_scholarly_book_modifier','Scholarly Manuscript','学术手稿','Manuscrit savant')
 L('CAUC_scholarly_book_modifier_desc','The work of a Caucasian scholar.','高加索学者的著述。','L’œuvre d’un savant du Caucase.')
 for key,words,desc in [
 ('CAUC_lori_book',('The Lori Disputation','《洛里论辩录》','La Dispute de Lori'),('Arguments and translations from the churches of Lori, preserved at the patron’s expense.','由赞助者出资保存的洛里教会论据与译文。','Arguments et traductions des Églises de Lori, conservés aux frais du mécène.')),
 ('CAUC_gelati_book',('Studies at Kutaisi','《库塔伊西学记》','Études de Koutaïssi'),('A bound volume prepared by the teachers near Kutaisi.','库塔伊西附近教师编写的装订书册。','Un volume relié composé par les maîtres des environs de Koutaïssi.')),
 ('CAUC_tondrakian_book',('Testimony of the Assemblies','《聚会见证录》','Témoignage des assemblées'),('The testimony of Smbat’s followers, including the women who spoke at the hearing.','斯姆巴特追随者的见证，包括听证中发言的女子。','Le témoignage des disciples de Smbat, dont les femmes entendues à l’audience.'))]:
  L(key,*words);L(key+'_desc',*desc)
 write(ROOT/'common/modifiers/CAUC_artifact_modifiers.txt','CAUC_scholarly_book_modifier = { icon = learning_positive learning = 1 }')
 for i,raw in enumerate(decisions):
  if entries(raw)[0][0]=='CAUC_derbent_guards_decision':decisions[i]=raw.replace('has_title = title:c_derbent '+M, 'has_title = title:c_derbent')
 F={x['flow']:x for x in flows};rus=F['derbent_guards']['policy_modifiers'];lori=F['lori_council']['policy_modifiers'];ani=F['ani_sanctuary']['policy_modifiers'];alan=F['alan_mission']['policy_modifiers']
 replacements={}
 replacements[100]=scene(100,'c_derbent','rus',
 ('[CAUC_rus_speaker.GetFirstName] sets a scarred shield at my feet. Five hundred Rus have followed this captain down the Caspian routes. He still swears by the Slavic gods: “My spear will guard your door if your coin feeds my men.” I can take him into my household, or contract his company without giving him a place beside my bedchamber.',
 '[CAUC_rus_speaker.GetFirstName]将一面伤痕累累的盾牌放在我脚边。五百名罗斯战士随这位队长沿里海商路而来。他依旧向斯拉夫诸神起誓：“你的钱养活我的人，我的矛便守住你的门。”我可以将他聘入内廷，也可以只雇用战团，不让他守在我的寝室旁。',
 '[CAUC_rus_speaker.GetFirstName] dépose à mes pieds un bouclier balafré. Cinq cents Rus ont suivi ce capitaine par les routes de la Caspienne. Il jure encore par les dieux slaves : « Votre or nourrira mes hommes ; ma lance gardera votre porte. » Je peux le prendre dans ma maisonnée, ou engager sa compagnie sans lui confier ma chambre.'),[
 (('You will be my bodyguard. Your men will join my army.','你来做我的贴身护卫，你的人加入我的军队。','Vous serez mon garde du corps ; vos hommes rejoindront mon armée.'),recruit('rus')+' appoint_court_position = { recipient = scope:CAUC_rus_speaker court_position = bodyguard_court_position } '+army()+opinion('rus',30)+chosen('c_derbent','rus_hired',1)+' '+nxt(101), 'is_valid_to_hire_court_position_type = bodyguard_court_position can_employ_court_position_type = bodyguard_court_position'),
 (('I need the five hundred soldiers, not a household guard.','我只雇用这五百名战士。','J’engage les cinq cents soldats.'),army()+chosen('c_derbent','rus_hired',0)+' '+nxt(101),'')],theme='martial')
 replacements[101]=scene(101,'c_derbent','rus',
 ('A preacher has gathered a crowd outside the barracks. “Will an unbeliever stand closer to our ruler than we do?” [CAUC_rus_speaker.GetFirstName] refuses to renounce his faith at swordpoint. His soldiers are already under contract; the quarrel now concerns his oath and his access to my household.',
 '传教士在营房外聚起人群：“一个异教徒，竟要站得比我们更靠近统治者？”[CAUC_rus_speaker.GetFirstName]拒绝在刀剑逼迫下改宗。战士们已经受雇，现在争的是队长的誓言，以及他能否进入我的内廷。',
 'Un prédicateur rassemble la foule devant les casernes. « Un infidèle sera-t-il plus proche de notre souverain que nous ? » [CAUC_rus_speaker.GetFirstName] refuse de renier sa foi sous la menace de l’épée. Ses soldats sont engagés ; le différend porte désormais sur son serment et son accès à ma maisonnée.'),[
 (('I will answer for his oath.','我为他的誓言担保。','Je répondrai de son serment.'),final_policy('c_derbent','derbent_guards',1,rus)+opinion('rus',35)+' add_piety = -75 '+nxt(102),''),
 (('Let him hear our teachers freely, without a forced conversion.','让他自由听取教导，不强迫改宗。','Qu’il écoute librement nos maîtres, sans conversion forcée.'),final_policy('c_derbent','derbent_guards',2,rus)+opinion('rus',10)+' add_learning_lifestyle_xp = 75 '+nxt(102),''),
 (('The company keeps its contract; the captain gets no special privilege.','战团照约效力，队长不享宗教特权。','La compagnie garde son contrat ; son capitaine n’aura aucun privilège religieux.'),final_policy('c_derbent','derbent_guards',3,rus)+opinion('rus',-30)+' add_piety = 50 '+nxt(102),'') ])
 replacements[102]=scene(102,'c_derbent','rus',
 ('The watch has been posted, but the captain waits for a public answer. The men will remember whether I stood beside them when the crowd shouted. A personal welcome will cost provisions; a curt order costs nothing, and promises little.',
 '值守已经安排妥当，队长却仍在等一个公开的答复。人群叫嚷时，我是否站在他们身旁，战士们都会记住。亲自款待需要粮食与酒；一纸命令不花钱，也给不了多少保证。',
 'Les postes de garde sont établis, mais le capitaine attend une réponse publique. Ses hommes se souviendront de ma présence lorsque la foule criait. Les accueillir coûte des provisions ; un ordre sec ne coûte rien et promet peu.'),[
 (('Share my table; there will be no doubt about my word.','来我的桌前同饮，我的承诺无需猜疑。','Partagez ma table ; ma parole ne laissera aucun doute.'),'remove_short_term_gold = 25 '+opinion('rus',25)+' '+end('derbent_guards'),'gold >= 25'),
 (('Your company has its orders.','你的战团已有命令。','Votre compagnie a ses ordres.'),opinion('rus',-10)+' '+end('derbent_guards'),'') ])
 # A lasting county policy records the settlement; the story itself changes people,
 # institutions, recruitment and artifacts rather than cycling temporary bonuses.
 replacements[110]=scene(110,'c_lori','abbot',
 ('[CAUC_abbot_speaker.GetFirstName] pushes the proposed agreement back across my table. Beside him, [CAUC_envoy_speaker.GetFirstName] opens a Greek manuscript. The abbot will not let a translator bargain away the prayers of his community. The envoy asks who will read the disputed words with him.',
 '[CAUC_abbot_speaker.GetFirstName]把协议推回桌子另一端。[CAUC_envoy_speaker.GetFirstName]在他身旁摊开希腊语手稿。院长不肯让译者拿本院的祷文作交易，使者则问，谁愿意与他一起读清那些有争议的字句？',
 '[CAUC_abbot_speaker.GetFirstName] repousse l’accord sur ma table. À ses côtés, [CAUC_envoy_speaker.GetFirstName] ouvre un manuscrit grec. L’abbé refuse qu’un traducteur négocie les prières de sa communauté. L’envoyé demande qui lira les passages contestés avec lui.'),[
 (('Abbot, remain here and defend your community’s prayers.','院长，你留下，为本院的祷文辩护。','Abbé, restez ici défendre les prières de votre communauté.'),chosen('c_lori','lori_council',1)+' '+recruit('abbot')+' '+opinion('abbot',25)+' '+nxt(111),''),
 (('The envoy will teach my scholars to read the original.','请使者教我的学者读原文。','L’envoyé apprendra à mes savants à lire l’original.'),chosen('c_lori','lori_council',2)+' '+recruit('envoy')+' '+opinion('envoy',25)+' '+nxt(111),''),
 (('Both shall be heard; I will pay for an independent translation.','双方都可发言，我出钱另译一份。','Les deux seront entendus ; je financerai une traduction indépendante.'),'remove_short_term_gold = 25 '+chosen('c_lori','lori_council',3)+' '+opinion('abbot',15)+' '+opinion('envoy',15)+' '+nxt(111),'gold >= 25')],C,'learning','CAUC_envoy_speaker_effect = yes')
 replacements[111]=scene(111,'c_lori','abbot',
 ('The second manuscript arrives with an angry note in the margin. A word rendered as “agreement” can also imply submission. [CAUC_abbot_speaker.GetFirstName] asks me to read the passage aloud. [CAUC_envoy_speaker.GetFirstName] offers lessons, but withdrawing the proposal would spare them both a humiliating signature.',
 '第二份手稿送来了，页边写着愤怒的批注：被译成“和议”的一个词，也可能意味着臣服。[CAUC_abbot_speaker.GetFirstName]请我把那一段读出来。[CAUC_envoy_speaker.GetFirstName]愿意教我；若撤回提议，两人便都不必在屈辱的文书上签名。',
 'Le second manuscrit arrive avec une note furieuse : le mot traduit par « accord » peut aussi signifier soumission. [CAUC_abbot_speaker.GetFirstName] me demande de lire le passage à voix haute. [CAUC_envoy_speaker.GetFirstName] propose de m’instruire ; retirer le texte éviterait aux deux une signature humiliante.'),[
 (('Teach me the words before I put my seal beneath them.','先教我读懂这些字句，再让我盖印。','Apprenez-moi ces mots avant que j’y appose mon sceau.'),'remove_short_term_gold = 20 add_learning_skill = 1 '+opinion('envoy',20)+' '+nxt(112),'gold >= 20'),
 (('Withdraw this wording. No one will sign under duress.','撤回这一措辞，不准强迫任何人签字。','Retirez cette formulation ; nul ne signera sous la contrainte.'),chosen('c_lori','lori_council',1)+' '+opinion('abbot',20)+' '+opinion('envoy',-10)+' '+nxt(112),'')],C,'learning','CAUC_envoy_speaker_effect = yes')
 lori_settle=' '.join('if = { limit = { title:c_lori = { var:CAUC_lori_council_choice = '+str(i)+' } } '+final_policy('c_lori','lori_council',i,lori)+' }' for i in (1,2,3))
 replacements[112]=scene(112,'c_lori','abbot',
 ('The disputants have kept their own churches. Their arguments, however, fill a new volume. [CAUC_abbot_speaker.GetFirstName] brings it wrapped in linen. I may take this record into my library, or give its makers a permanent place among my household scholars.',
 '双方仍各守自己的教会，但论辩已写满了一册新书。[CAUC_abbot_speaker.GetFirstName]用亚麻布包好，送到我面前。我可以把这份记录收入藏书，也可以让编写者留在内廷，从此为我讲学。',
 'Les deux parties conservent leurs Églises, mais leurs arguments remplissent un nouveau volume. [CAUC_abbot_speaker.GetFirstName] l’apporte enveloppé de lin. Je peux l’accueillir dans ma bibliothèque ou donner à ses auteurs une place durable parmi mes savants.'),[
 (('Bind the disputation for my library.','将论辩装订成册，收入我的藏书。','Reliez la dispute pour ma bibliothèque.'),'remove_short_term_gold = 30 '+book('CAUC_lori_book','abbot')+' '+end('lori_council'),'gold >= 30'),
 (('The abbot will remain as my teacher.','院长留下，做我的老师。','L’abbé restera comme mon maître.'),recruit('abbot')+' '+opinion('abbot',30)+' '+end('lori_council'),'')],C,'learning',lori_settle)
 replacements[120]=scene(120,'c_hayk','warden',
 ('[CAUC_warden_speaker.GetFirstName] lays the cathedral keys beside a worn dedication. [CAUC_imam_speaker.GetFirstName] produces the deed granted to the mosque. Both have worshippers waiting outside. Whoever loses the building will need a home for their prayers, and both men demand a judgment they can carry back to the street.',
 '[CAUC_warden_speaker.GetFirstName]把主教座堂的钥匙放在一份磨损的祝圣文书旁。[CAUC_imam_speaker.GetFirstName]拿出了清真寺获授的契据。两人的会众都在门外等候。失去建筑的一方需要新的礼拜之所，两人也都要求一个能向街上人群交代的裁决。',
 '[CAUC_warden_speaker.GetFirstName] dépose les clefs de la cathédrale auprès d’un acte de consécration usé. [CAUC_imam_speaker.GetFirstName] présente le titre accordé à la mosquée. Leurs fidèles attendent dehors. Les perdants auront besoin d’un lieu de prière ; les deux hommes exigent un jugement qu’ils pourront annoncer dans la rue.'),[
 (('Return the cathedral keys to its Christian keeper.','把主教座堂钥匙交还基督徒管理人。','Rendez les clefs au gardien chrétien.'),'remove_short_term_gold = 25 '+chosen('c_hayk','ani_sanctuary_use',1)+' '+chosen('c_hayk','ani_sanctuary',1)+' '+opinion('warden',30)+' '+opinion('imam',-25)+' '+nxt(121),'gold >= 25'),
 (('Confirm the mosque’s deed and its endowment.','确认清真寺的契据与捐产。','Confirmez le titre et la dotation de la mosquée.'),'remove_short_term_gold = 25 '+chosen('c_hayk','ani_sanctuary_use',2)+' '+chosen('c_hayk','ani_sanctuary',2)+' '+opinion('imam',30)+' '+opinion('warden',-25)+' '+nxt(121),'gold >= 25'),
 (('The present congregation keeps the keys; neither side may expel the other.','钥匙留在现有会众手里，双方都不得驱逐对方。','La communauté actuelle garde les clefs ; nul ne chassera l’autre.'),chosen('c_hayk','ani_sanctuary',3)+' '+opinion('warden',10)+' '+opinion('imam',10)+' '+nxt(121),'')],theme='stewardship',immediate='CAUC_imam_speaker_effect = yes')
 replacements[121]=scene(121,'c_hayk','warden',
 ('The judgment has divided the street. [CAUC_warden_speaker.GetFirstName] and [CAUC_imam_speaker.GetFirstName] ask who will guarantee safe passage to prayer. I can bring both men to my court to negotiate, or post a watch while their followers find separate rooms.',
 '裁决令街上的人群分成了两派。[CAUC_warden_speaker.GetFirstName]与[CAUC_imam_speaker.GetFirstName]追问：谁来保证信徒能平安前往礼拜？我可以把两人请入宫廷继续协商，或派人值守，让会众各自寻找房舍。',
 'Le jugement divise la rue. [CAUC_warden_speaker.GetFirstName] et [CAUC_imam_speaker.GetFirstName] demandent qui protégera le chemin des fidèles. Je peux les recevoir à ma cour pour négocier ou poster une garde pendant que leurs communautés trouvent des salles séparées.'),[
 (('Both spokesmen will negotiate under my roof.','两位代表都在我的屋檐下协商。','Les deux représentants négocieront sous mon toit.'),recruit('warden')+' '+recruit('imam')+' '+opinion('warden',15)+' '+opinion('imam',15)+' '+nxt(122),''),
 (('Pay a watch to protect the congregations.','出钱派人保护双方会众。','Payez une garde pour protéger les fidèles.'),'remove_short_term_gold = 20 title:c_hayk = { change_county_control = 8 } '+nxt(122),'gold >= 20'),
 (('Their elders must keep the peace.','由各自长老维持秩序。','Leurs anciens maintiendront la paix.'),'title:c_hayk = { change_county_control = -5 } '+nxt(122),'')],immediate='CAUC_imam_speaker_effect = yes')
 ani_settle=' '.join('if = { limit = { title:c_hayk = { var:CAUC_ani_sanctuary_choice = '+str(i)+' } } '+final_policy('c_hayk','ani_sanctuary',i,ani)+' }' for i in (1,2,3))
 replacements[122]=scene(122,'c_hayk','warden',
 ('The keys have found their keeper. The other community has cleared an empty room, but its roof leaks. [CAUC_warden_speaker.GetFirstName] and [CAUC_imam_speaker.GetFirstName] return together: one carrying his deed, the other a list of timber. My judgment can leave a usable place to pray, or merely a locked door.',
 '钥匙已有归属。另一方会众清出了一间空屋，屋顶却在漏雨。[CAUC_warden_speaker.GetFirstName]与[CAUC_imam_speaker.GetFirstName]一同回来，一个拿着契据，一个拿着木料清单。我的裁决可以留下能用的礼拜房舍，也可能只剩一扇锁上的门。',
 'Les clefs ont trouvé leur gardien. L’autre communauté a dégagé une salle dont le toit fuit. [CAUC_warden_speaker.GetFirstName] et [CAUC_imam_speaker.GetFirstName] reviennent ensemble, l’un avec son titre, l’autre avec une liste de bois. Mon jugement peut laisser un lieu de prière utilisable, ou seulement une porte close.'),[
 (('Repair the displaced congregation’s roof.','为迁出的会众修好屋顶。','Réparez le toit de la communauté déplacée.'),'remove_short_term_gold = 25 '+opinion('warden',25)+' '+opinion('imam',25)+' title:c_hayk = { change_county_control = 8 } '+end('ani_sanctuary'),'gold >= 25'),
 (('Let the two keepers administer these promises together.','让两位管理人一起兑现这些承诺。','Que les deux gardiens administrent ensemble ces garanties.'),recruit('warden')+' '+recruit('imam')+' '+end('ani_sanctuary'),'')],immediate='CAUC_imam_speaker_effect = yes '+ani_settle)
 replacements[130]=scene(130,'c_maghas','missionary',
 ('[CAUC_missionary_speaker.GetFirstName] opens a gospel before the elders. [CAUC_elder_speaker.GetFirstName] stops him before he names a site for his church: “That ground holds the oaths of our families.” The missionary offers a teacher for my household; the elder offers riders who know every northern pass.',
 '[CAUC_missionary_speaker.GetFirstName]在长老面前打开福音书。还没说出教堂的选址，[CAUC_elder_speaker.GetFirstName]就打断了他：“那片土地维系着我们各家的誓约。”传教士愿为我的内廷提供教师，长老则许诺派来熟悉北方每一条山道的骑手。',
 '[CAUC_missionary_speaker.GetFirstName] ouvre un évangile devant les anciens. [CAUC_elder_speaker.GetFirstName] l’arrête avant qu’il ne choisisse l’emplacement de son église : « Ce sol porte les serments de nos familles. » Le missionnaire propose un maître pour ma maisonnée ; l’ancien offre des cavaliers connaissant chaque col du nord.'),[
 (('The missionary will teach at my court, on land I grant.','传教士在我的宫廷讲学，我来提供土地。','Le missionnaire enseignera à ma cour, sur les terres que je lui accorde.'),'remove_short_term_gold = 25 '+recruit('missionary')+' '+opinion('missionary',30)+' '+opinion('elder',-20)+' '+chosen('c_maghas','alan_mission',1)+' '+nxt(131),'gold >= 25'),
 (('Both will remain and answer to one another.','双方都留下，彼此答辩。','Les deux resteront pour se répondre.'),recruit('missionary')+' '+recruit('elder')+' '+opinion('elder',20)+' '+chosen('c_maghas','alan_mission',2)+' '+nxt(131),''),
 (('Elder, bring your riders. The mission has no grant.','长老，带你的骑手来；使团不会得到拨地。','Ancien, amenez vos cavaliers. La mission ne recevra aucune terre.'),recruit('elder')+' spawn_army = { name = CAUC_alan_event_army men_at_arms = { type = light_horsemen stacks = 2 } location = root.capital_province inheritable = no war_keep_on_attacker_victory = yes } '+opinion('elder',30)+' '+opinion('missionary',-30)+' '+chosen('c_maghas','alan_mission',3)+' '+nxt(131),'')],immediate='CAUC_elder_speaker_effect = yes')
 replacements[131]=scene(131,'c_maghas','elder',
 ('[CAUC_elder_speaker.GetFirstName] brings a broken boundary stake. Someone has moved it overnight; the missionary’s pupils were seen nearby. [CAUC_missionary_speaker.GetFirstName] denies ordering it. A feud may begin over a few paces of earth. I must demand restitution or insist that my earlier grant stands.',
 '[CAUC_elder_speaker.GetFirstName]带来了一根断裂的界桩。有人夜里挪动了它，传教士的学生曾在附近出现。[CAUC_missionary_speaker.GetFirstName]否认下过命令。几步宽的土地就可能引发仇杀；我必须要求赔偿，或坚持先前的拨地。',
 '[CAUC_elder_speaker.GetFirstName] apporte une borne brisée. Quelqu’un l’a déplacée dans la nuit ; les élèves du missionnaire ont été vus près d’elle. [CAUC_missionary_speaker.GetFirstName] nie l’avoir ordonné. Quelques pas de terre peuvent déclencher une vendetta. Je dois exiger réparation ou maintenir ma concession.'),[
 (('Restore the marker at my expense.','由我出钱恢复界桩。','Rétablissez la borne à mes frais.'),'remove_short_term_gold = 20 '+opinion('elder',25)+' '+opinion('missionary',10)+' title:c_maghas = { change_county_control = 8 } '+nxt(132),'gold >= 20'),
 (('The mission must yield the disputed ground.','使团必须让出争议土地。','La mission doit céder le terrain contesté.'),chosen('c_maghas','alan_mission',2)+' '+opinion('elder',20)+' '+opinion('missionary',-20)+' '+nxt(132),''),
 (('My grant stands. Take this grievance to my officers.','拨地照旧，将申诉交给我的官员。','Ma concession demeure. Adressez votre plainte à mes officiers.'),opinion('elder',-25)+' title:c_maghas = { change_county_control = -8 } '+nxt(132),'')],immediate='CAUC_missionary_speaker_effect = yes')
 alan_settle=' '.join('if = { limit = { title:c_maghas = { var:CAUC_alan_mission_choice = '+str(i)+' } } '+final_policy('c_maghas','alan_mission',i,alan)+' }' for i in (1,2,3))
 replacements[132]=scene(132,'c_maghas','missionary',
 ('The boundary has been settled. [CAUC_missionary_speaker.GetFirstName] asks for my own answer to his teaching. [CAUC_elder_speaker.GetFirstName] waits at the doorway, unwilling to offer a prayer on my behalf. If I accept baptism, this will be my choice, not a decree converting every family in Alania.',
 '界线已经裁定。[CAUC_missionary_speaker.GetFirstName]请我亲自回应他的教导。[CAUC_elder_speaker.GetFirstName]等在门口，不愿代我作出信仰的承诺。若我接受洗礼，那是我自己的选择，并非命令阿兰所有家族一同改宗。',
 'La frontière est fixée. [CAUC_missionary_speaker.GetFirstName] attend ma réponse personnelle à son enseignement. [CAUC_elder_speaker.GetFirstName] demeure à la porte, refusant de prier en mon nom. Accepter le baptême sera mon choix, non un décret convertissant toutes les familles d’Alanie.'),[
 (('I will receive baptism into the missionary’s faith.','我将受洗，接受传教士的信仰。','Je recevrai le baptême dans la foi du missionnaire.'),'set_character_faith = faith:orthodox '+opinion('missionary',50)+' '+opinion('elder',-20)+' '+end('alan_mission'),'NOT = { faith = faith:orthodox }'),
 (('Stay as a teacher; belief cannot be commanded.','留下做教师，信仰不可强求。','Restez comme maître ; la foi ne se commande pas.'),recruit('missionary')+' add_learning_skill = 1 '+end('alan_mission'),''),
 (('I will ride with the elders and keep my own worship.','我与长老同骑，保留自己的信仰。','Je chevaucherai avec les anciens et garderai ma foi.'),recruit('elder')+' add_martial_lifestyle_xp = 150 '+opinion('elder',25)+' '+end('alan_mission'),'')],immediate='CAUC_elder_speaker_effect = yes '+alan_settle)
 L('CAUC_alan_event_army','Riders of the Northern Passes','北方山道骑手','Cavaliers des cols du nord')
 # Keep the doctrinal hearing, but make its witness, rents and judgment consequential.
 for n,raw in enumerate(events):
  key=entries(raw)[0][0];number=int(key.split('.')[1])
  if number in replacements:events[n]=replacements[number];continue
  if 140<=number<=144:
   raw=replace_field(raw,'immediate','CAUC_tondrakian_recover_speaker_effect = yes CAUC_tondrakian_witness_effect = yes')
   if number==141:
    raw=raw.replace('add_learning_lifestyle_xp = 75',recruit('representative')+' '+opinion('representative',35)+' add_learning_lifestyle_xp = 75')
    L(key+'.desc',
     '[CAUC_representative_speaker.GetFirstName] steps out from behind Smbat’s followers. The envoy orders her to be silent, but she puts the rent accounts on my table herself. “If I can keep these fields alive, I can speak for those who work them.” Letting her answer gives the assemblies a representative in my household.',
     '[CAUC_representative_speaker.GetFirstName]从斯姆巴特的追随者中走出。使者命令她闭嘴，她却亲手把租赋账册放到我桌上：“我能让田地养活众人，也能替耕种的人说话。”允许她答辩，就意味着给聚会社群一位能在我的内廷发言的代表。',
     '[CAUC_representative_speaker.GetFirstName] sort du groupe des disciples de Smbat. L’envoyé lui ordonne de se taire, mais elle pose elle-même les comptes sur ma table. « Si je peux faire vivre ces champs, je peux parler pour ceux qui les cultivent. » L’entendre donnera aux assemblées une représentante dans ma maisonnée.')
    raw=replace_field(raw,'right_portrait','character = scope:CAUC_representative_speaker')
   if number==142:
    raw=raw.replace('change_county_control = 5','change_county_control = 5 set_variable = { name = CAUC_tondrakian_land_survey value = 1 }')
    raw=raw.replace('remove_short_term_gold = 10 add_prestige = -15','remove_short_term_gold = 10 '+opinion('representative',25))
   if number==143:
    raw=raw.replace('add_piety = -100',recruit('tondrakian')+' '+opinion('tondrakian',35)+' add_piety = -100')
    # A suppression imprisons the living speaker, not a fabricated off-screen mob.
    raw=raw.replace('add_piety = 100','imprison = { target = scope:CAUC_tondrakian_speaker type = dungeon } '+opinion('representative',-50)+' add_piety = 100')
    raw=raw.replace('add_piety = -500',recruit('tondrakian')+' '+recruit('representative')+' add_piety = -500')
   if number==144:
    raw=raw.replace('remove_short_term_gold = 15 add_learning_lifestyle_xp = 75','remove_short_term_gold = 15 '+book('CAUC_tondrakian_book','representative'))
    # Do not offer a celebratory charter to a ruler whose previous verdict was suppression.
    raw=raw.replace('trigger = { gold >= 15 }','trigger = { gold >= 15 NOT = { title:c_apahunik = { var:CAUC_tondrakian_inquiry_choice = 5 } } }')
   events[n]=raw
 # Do not claim troops were dismissed when the contract remains in force.
 L('CAUC_rus_dismissed','Restricted Rus Privileges','罗斯特权受限','Privilèges rus’ limités')
 L('CAUC_rus_dismissed_desc','The company keeps its military contract, but its captain receives no guarantee of separate religious privileges.','战团仍按军约效力，但队长未获另享宗教特权的保障。','La compagnie conserve son contrat militaire, sans garantie de privilèges religieux distincts pour son capitaine.')
 # Native modifier metadata colors names as well as drawing the icons.
 for i,raw in enumerate(modifiers):
  name=entries(raw)[0][0]
  negative=name in ('CAUC_rus_dismissed','CAUC_tondrakian_suppressed','CAUC_alan_mission_dismissed')
  icon='county_modifier_opinion_'+('negative' if negative else 'positive')
  modifiers[i]=raw.replace('{','{ icon = '+icon,1)
 # Dated global foundation, independent of religion, county ownership and chance.
 L('CAUC.0150.t','A New Rite at Tondrak','通德拉克的新礼制','Un nouveau rite à Tondrak')
 L('CAUC.0150.desc',
  '[CAUC_tondrakian_speaker.GetFullName] has begun preaching among the Armenian villages near Tondrak. His followers gather without holy images, hold property in common and deny that men and women stand differently before God. Churchmen demand his silence. His rite now has a name; rulers in Apahunik may hear his followers and decide whether to protect, imprison or join them.',
  '[CAUC_tondrakian_speaker.GetFullName]已在通德拉克附近的亚美尼亚村庄讲道。追随者不设圣像、共同持有财产，并否认男女在上帝面前有不同地位。教会要求他噤声。他的礼制如今已有名称；阿帕胡尼克的统治者可以听取追随者的陈述，决定庇护、囚禁，或加入他们。',
  '[CAUC_tondrakian_speaker.GetFullName] prêche dans les villages arméniens près de Tondrak. Ses disciples se réunissent sans images, partagent leurs biens et affirment l’égalité des hommes et des femmes devant Dieu. L’Église exige son silence. Son rite porte désormais un nom ; les dirigeants d’Apahunik peuvent entendre ses disciples, les protéger, les emprisonner ou les rejoindre.')
 L('CAUC.0150.b','I will join this Armenian rite.','我将加入这一亚美尼亚礼制。','Je rejoindrai ce rite arménien.')
 L('CAUC.0150.a','Word of these assemblies will spread.','这些聚会的消息会传开。','La nouvelle de ces assemblées se répandra.')
 events.append('''CAUC.0149 = { hidden = yes trigger = { NOT = { has_global_variable = CAUC_tondrakian_outbreak_announced } } immediate = {
 set_global_variable = { name = CAUC_tondrakian_outbreak_announced value = yes }
 CAUC_tondrakian_prepare_inquiry_effect = yes
 if = { limit = { game_start_date = 867.1.1 }
  every_player = { trigger_event = { id = CAUC.0150 days = 1 } }
  if = { limit = { is_landed = yes is_available_adult = yes is_imprisoned = no has_title = title:c_apahunik faith = { religion = religion:christianity_religion } NOT = { has_character_flag = CAUC_tondrakian_inquiry_active } }
   add_character_flag = { flag = CAUC_tondrakian_inquiry_active years = 1 }
   trigger_event = { id = CAUC.0140 days = 14 }
  }
 } }
}''')
 events.append('''CAUC.0150 = { type = character_event title = CAUC.0150.t desc = CAUC.0150.desc theme = learning
 right_portrait = { character = scope:CAUC_tondrakian_speaker }
 trigger = { exists = global_var:CAUC_tondrakian_founder }
 immediate = { global_var:CAUC_tondrakian_founder = { save_scope_as = CAUC_tondrakian_speaker } }
 option = { name = CAUC.0150.a }
 option = { name = CAUC.0150.b trigger = { is_landed = yes is_available_adult = yes is_imprisoned = no faith = faith:armenian_apostolic piety >= 500 capital_province = { geographical_region = CAUC_transcaucasia_region } } add_piety = -500 set_character_rite = rite:CAUC_tondrakian_rite }
}''')
 # The hidden scheduler is an additive on-action; no random pulse or paid decision.
 write(ROOT/'common/on_action/CAUC_tondrakian_start_on_actions.txt','''on_game_start_after_lobby = { on_actions = { CAUC_tondrakian_start } }
CAUC_tondrakian_start = {
 effect = {
  if = { limit = { NOT = { has_global_variable = CAUC_tondrakian_scheduled } }
   set_global_variable = { name = CAUC_tondrakian_scheduled value = yes }
   title:c_apahunik.holder = {
    if = { limit = { game_start_date = 867.1.1 }
     trigger_event = { id = CAUC.0149 days = 365 }
    }
    else = { CAUC_tondrakian_prepare_inquiry_effect = yes }
   }
  }
 }
}
yearly_global_pulse = { on_actions = { CAUC_tondrakian_guaranteed_outbreak } }
CAUC_tondrakian_guaranteed_outbreak = {
 trigger = { game_start_date = 867.1.1 current_date >= 868.1.1 NOT = { has_global_variable = CAUC_tondrakian_outbreak_announced } }
 effect = { title:c_apahunik.holder = { trigger_event = { id = CAUC.0149 days = 1 } } }
}
''')
 L('CAUC_derbent_guards_decision_tooltip','Meet a Slavic Rus captain and recruit 500 event troops. Hire him as an Excellent bodyguard if a position is available, or retain only the company.','接见一名斯拉夫信仰的罗斯队长，招募500名事件兵。若有空缺，可聘为极佳称职度的贴身护卫；也可只雇用战团。','Rencontrer un capitaine rus’ slave et recruter 500 soldats. Un poste libre permet d’en faire un excellent garde du corps ; sinon, seule la compagnie est engagée.')
 L('CAUC_alan_mission_decision_tooltip','Meet an Orthodox missionary and an Alan elder. Recruit a teacher or northern riders, resolve their boundary dispute, and choose whether to accept baptism personally.','接见正教传教士与阿兰长老，延请教师或招募北方骑手，裁定土地争执，并决定自己是否受洗。','Rencontrer un missionnaire orthodoxe et un ancien alain ; engager un maître ou des cavaliers, régler leur frontière et décider d’un baptême personnel.')
 # Revise all smaller regional scenes as well: recurring named contacts, real
 # recruits and tangible manuscripts; the county remains the availability gate.
 p=ROOT/'events/CAUC_regional_events.txt'
 import json
 base=json.loads((ROOT/'research/regional-scenes-base.json').read_text())
 text=base['events/CAUC_regional_events.txt']
 edited=[]
 for key,body,a,z in entries(text):
  if key=='namespace':continue
  raw=text[a:z];number=int(key.split('.')[1]);role='scholar' if number in (2,4) or 20<=number<=25 else ('mason' if number==3 or 30<=number<=35 else 'overseer')
  raw=replace_field(raw,'immediate','CAUC_'+role+'_speaker_effect = yes')
  raw=replace_field(raw,'right_portrait','character = scope:CAUC_'+role+'_speaker')
  # Existing translated prose is retained; all languages get the same visible contact.
  for lang in LANGS:
   lp=ROOT/'localization'/lang/('CAUC_flavor_l_'+lang+'.yml')
   import re
   old=re.search(r'^ '+re.escape(key+'.desc')+r':\d+ "(.*)"$',base['localization/'+lang+'/CAUC_flavor_l_'+lang+'.yml'],re.M)
   prefix={'english':f'[CAUC_{role}_speaker.GetFirstName] brings this matter before me. ', 'simp_chinese':f'[CAUC_{role}_speaker.GetFirstName]来到我面前，陈述此事。','french':f'[CAUC_{role}_speaker.GetFirstName] me soumet cette affaire. '}[lang]
   if old:loc[lang][key+'.desc']=prefix+old[1]
  # Artifact outcomes belong to scholarly work; other cases introduce a skilled
  # steward or mason to the court, instead of another temporary numeric modifier.
  if role=='scholar':
   name=key+'.d';L(name,'Commission a bound manuscript for my library.','请学者编成手稿，收入我的藏书。','Commander un manuscrit relié pour ma bibliothèque.')
   effect='remove_short_term_gold = 30 '+book('CAUC_gelati_book' if number==4 else 'CAUC_lori_book','scholar');gate='gold >= 30'
  else:
   name=key+'.d';L(name,'Offer this skilled representative a place at my court.','请这位能干的代表到我的宫廷效力。','Offrir une place à ma cour à ce représentant compétent.')
   effect=recruit(role)+' '+opinion(role,25)
   if number==1:effect+=' title:c_derbent = { remove_county_modifier = CAUC_pass_trade remove_county_modifier = CAUC_pass_guard remove_county_modifier = CAUC_pass_compact add_county_modifier = { modifier = CAUC_pass_compact years = 5 } }'
   gate='NOT = { scope:CAUC_'+role+'_speaker = { is_courtier_of = root } }'
  raw=raw[:raw.rfind('}')]+f' option = {{ name = {name} trigger = {{ {gate} }} {effect} ai_chance = {{ base = 30 }} }}\n}}'
  edited.append(raw)
 write(p,'namespace = CAUC\n\n'+'\n\n'.join(edited))
 # Updated text is written in one authoritative localization file, avoiding duplicate keys.
 for lang in LANGS:
  lp=ROOT/'localization'/lang/('CAUC_flavor_l_'+lang+'.yml')
  lines=lp.read_text(encoding='utf-8-sig').splitlines()
  import re
  lines=[line for line in lines if not (re.match(r'\s+(\S+):\d+ ',line) and re.match(r'\s+(\S+):\d+ ',line)[1] in loc[lang])]
  write(lp,'\n'.join(lines))
 # Add proper native icons to all existing regional bonuses and penalties too.
 p=ROOT/'common/modifiers/CAUC_regional_modifiers.txt';text=base['common/modifiers/CAUC_regional_modifiers.txt'];out=[]
 for key,body,a,z in entries(text):
  icon='economy_negative' if key=='CAUC_pass_obstructed' else ('martial_positive' if 'fort_level' in body else ('economy_positive' if 'tax_mult' in body else 'county_modifier_development_positive'))
  out.append(key+' = { icon = '+icon+' '+body+' }')
 write(p,'\n\n'.join(out))

"""Offer regional rulers an opt-in response chain while Apahunik resolves the case."""
from ck3_script import entries

def extend(events, loc):
 from overhaul_stories import replace_field
 def L(key,en,zh,fr):
  for lang,value in zip(('english','simp_chinese','french'),(en,zh,fr)):loc[lang][key]=value
 gate='CAUC_tondrakian_broadcast_recipient_trigger = yes is_available_adult = yes is_imprisoned = no NOT = { rite = rite:CAUC_tondrakian_rite } NOT = { any_held_title = { has_clerical_region = yes } }'
 join='option = { name = CAUC.0150.b trigger = { '+gate+' } CAUC_tondrakian_join_effect = yes ai_chance = { base = 5 modifier = { factor = 8 CAUC_tondrakian_armenian_crown_vassal_trigger = yes } } }'
 for i,raw in enumerate(events):
  key,body,_,_=entries(raw)[0];number=int(key.split('.')[1])
  if 141<=number<=144:
   immediate=next(v for k,v,a,z in entries(body) if k=='immediate')
   raw=replace_field(raw,'immediate',immediate+f' save_scope_value_as = {{ name = CAUC_tondrakian_news_stage value = {number} }} CAUC_tondrakian_broadcast_followup_effect = yes')
  if number==140:
   immediate=next(v for k,v,a,z in entries(body) if k=='immediate')
   raw=replace_field(raw,'immediate',immediate+' set_global_variable = { name = CAUC_tondrakian_inquiry_started value = yes }')
  if number==149:
   raw=raw.replace(' CAUC_tondrakian_seed_counties_effect = yes',' CAUC_tondrakian_seed_counties_effect = yes\n set_global_variable = { name = CAUC_tondrakian_public_sequel_initialized value = yes }',1)
   start=raw.index('  title:c_apahunik = {');end=raw.index('  if = { limit = { is_landed',start)
   raw=raw[:start]+'''  every_ruler = {
   limit = { is_ai = yes CAUC_tondrakian_broadcast_recipient_trigger = yes }
   trigger_event = { id = CAUC.0150 days = 8 }
  }
'''+raw[end:]
   raw=raw.replace('  every_ruler = {','  faith:armenian_apostolic = { trigger_event = { id = CAUC.0152 days = 45 } }\n  every_ruler = {',1)
  if number==150:
   start=raw.index(' option = { name = CAUC.0150.a')
   raw=raw[:start]+' option = { name = CAUC.0150.a ai_chance = { base = 100 } }\n '+join+'\n}'
  events[i]=raw
 L('CAUC.0151.t','News of the Tondrakian Assemblies','通德拉基聚会的消息','Nouvelles des assemblées tondrakiennes')
 L('CAUC.0151.women','A woman from the assemblies has appeared before [CAUC_tondrakian_host.GetTitledFirstName]. She claims the same standing as men before God, and speaks for the families who shelter Smbat’s followers. Her testimony is now carried to the Christian courts of the Caucasus.','一位聚会中的女子来到[CAUC_tondrakian_host.GetTitledFirstName]面前。她宣称男女在上帝面前地位平等，并代表庇护斯姆巴特追随者的家庭发言。她的证词如今传到了高加索的基督教宫廷。','Une femme des assemblées a témoigné devant [CAUC_tondrakian_host.GetTitledFirstName]. Elle affirme que femmes et hommes sont égaux devant Dieu et parle pour les familles qui abritent les disciples de Smbat. Son témoignage circule dans les cours chrétiennes du Caucase.')
 L('CAUC.0151.land','[CAUC_tondrakian_host.GetTitledFirstName] is examining the fields shared by the assemblies. Villagers claim that land and harvest belong to the community; churchmen produce deeds and demand rents. Messengers bring both accounts to my court.','[CAUC_tondrakian_host.GetTitledFirstName]正在调查聚会共同耕种的田地。村民主张土地与收成归共同体所有，教士则出示地契、要求缴租。使者把双方的说法带到了我的宫廷。','[CAUC_tondrakian_host.GetTitledFirstName] examine les champs des assemblées. Les villageois revendiquent la propriété commune des terres et des récoltes ; les clercs présentent des titres et exigent des loyers. Des messagers apportent les deux récits à ma cour.')
 L('CAUC.0151.prohibition','Armenian churchmen demand that [CAUC_tondrakian_host.GetTitledFirstName] close the assemblies. Smbat’s followers reject holy images and clerical authority. The local ruler must now decide whether to protect them, imprison their preacher or embrace the new rite.','亚美尼亚教士要求[CAUC_tondrakian_host.GetTitledFirstName]取缔聚会。斯姆巴特的追随者拒绝圣像与神职权威。当地统治者必须决定庇护他们、囚禁讲道者，还是接纳新礼仪。','Les clercs arméniens exigent que [CAUC_tondrakian_host.GetTitledFirstName] ferme les assemblées. Les disciples de Smbat rejettent les images sacrées et l’autorité du clergé. Le dirigeant doit les protéger, emprisonner leur prédicateur ou embrasser le nouveau rite.')
 L('CAUC.0151.suppressed','[CAUC_tondrakian_host.GetTitledFirstName] has closed the assemblies and imprisoned their preacher. Families who sheltered them fear further arrests. News of the prohibition has crossed the Caucasian passes; I must decide how to receive the rite in my own lands.','[CAUC_tondrakian_host.GetTitledFirstName]取缔了聚会，并囚禁了讲道者。曾庇护他们的家庭担忧更多逮捕。禁令的消息已经越过高加索山口；我必须决定如何在自己的领地对待这一礼仪。','[CAUC_tondrakian_host.GetTitledFirstName] a fermé les assemblées et emprisonné leur prédicateur. Les familles qui les abritaient craignent de nouvelles arrestations. La nouvelle a franchi les cols du Caucase ; je dois décider comment accueillir ce rite dans mes terres.')
 L('CAUC.0151.adopted','[CAUC_tondrakian_host.GetTitledFirstName] has embraced the Tondrakian rite. Congregations and members of the court have followed the ruler’s example. The assemblies now have a patron, though the Armenian Church still disputes their teachings.','[CAUC_tondrakian_host.GetTitledFirstName]接纳了通德拉基礼仪，信众与宫廷成员也随之改奉。聚会如今得到统治者支持，亚美尼亚教会却仍质疑他们的教诲。','[CAUC_tondrakian_host.GetTitledFirstName] a embrassé le rite tondrakien. Des fidèles et des membres de la cour ont suivi cet exemple. Les assemblées ont désormais un protecteur, bien que l’Église arménienne conteste toujours leurs enseignements.')
 L('CAUC.0151.protected','[CAUC_tondrakian_host.GetTitledFirstName] has allowed the assemblies to continue without adopting their rite. Their testimony is being recorded, and their preacher has found protection. Their teaching may yet take root elsewhere in the Caucasus.','[CAUC_tondrakian_host.GetTitledFirstName]允许聚会继续，却没有改奉其礼仪。证词正在编录，讲道者也获得庇护。他们的教诲或许还会在高加索其他地方扎根。','[CAUC_tondrakian_host.GetTitledFirstName] permet aux assemblées de continuer sans adopter leur rite. Leurs témoignages sont consignés et leur prédicateur a trouvé protection. Leur enseignement pourrait encore prendre racine ailleurs dans le Caucase.')
 L('CAUC.0151.a','I will hear their testimony.','我会听取他们的见证。','J’écouterai leur témoignage.')
 L('CAUC.0151.b','Rebuke these heretics. I will hear no more until judgment is passed.','斥责这些异端。在裁决作出前，我不愿再听到他们的消息。','Réprimander ces hérétiques. Je ne veux plus en entendre parler avant le jugement.')
 L('CAUC.0151.land_a','Let the villagers present their claim to the harvest.','让村民陈述他们对收成的主张。','Que les villageois présentent leurs droits sur la récolte.')
 L('CAUC.0151.land_b','The Church’s deeds must carry lawful weight.','教会的地契应当具有法律效力。','Les titres de l’Église doivent avoir force de loi.')
 L('CAUC.0151.prohibition_a','Assemblies seeking my protection will be heard.','寻求我庇护的聚会可以陈述自己的主张。','Les assemblées qui sollicitent ma protection seront entendues.')
 L('CAUC.0151.prohibition_b','I condemn their teaching and close my court to their messengers.','我谴责他们的教义，并禁止其使者再入宫廷。','Je condamne leur doctrine et ferme ma cour à leurs messagers.')
 L('CAUC.0151.result','Now I know how the judgment fell.','现在我知道裁决的结果了。','Je connais désormais l’issue du jugement.')
 L('CAUC.0151.unresolved','The assemblies continue to draw followers in Apahunik. Churchmen demand a prohibition, while villagers insist that their testimony be heard. No settlement has yet been announced. Their dispute is now discussed in Christian courts on both sides of the Caucasus.','阿帕胡尼克的聚会仍在吸引信众。教士要求禁绝，村民却坚持自己的证词应当得到听取。尚无正式处置公布。高加索南北的基督教宫廷如今都在议论这场争端。','Les assemblées continuent d’attirer des disciples en Apahunik. Les clercs réclament une interdiction, tandis que les villageois demandent à être entendus. Aucun règlement n’a été annoncé. Leur querelle est discutée dans les cours chrétiennes des deux versants du Caucase.')
 events.append('''CAUC.0151 = {
 type = character_event title = CAUC.0151.t theme = faith
 desc = { first_valid = {
  triggered_desc = { trigger = { scope:CAUC_tondrakian_news_stage = 141 } desc = CAUC.0151.women }
  triggered_desc = { trigger = { scope:CAUC_tondrakian_news_stage = 142 } desc = CAUC.0151.land }
  triggered_desc = { trigger = { scope:CAUC_tondrakian_news_stage = 143 } desc = CAUC.0151.prohibition }
  triggered_desc = { trigger = { title:c_apahunik = { var:CAUC_tondrakian_inquiry_choice = 5 } } desc = CAUC.0151.suppressed }
  triggered_desc = { trigger = { title:c_apahunik = { var:CAUC_tondrakian_inquiry_choice = 6 } } desc = CAUC.0151.adopted }
  triggered_desc = { trigger = { title:c_apahunik = { var:CAUC_tondrakian_inquiry_choice = 4 } } desc = CAUC.0151.protected }
  desc = CAUC.0151.unresolved
 } }
 widget = { gui = "event_window_widget_rite_founder" container = "custom_widgets_container" }
 left_portrait = { character = scope:CAUC_tondrakian_host }
 trigger = { exists = global_var:CAUC_tondrakian_founder exists = scope:CAUC_tondrakian_host CAUC_tondrakian_broadcast_recipient_trigger = yes }
 immediate = { CAUC_tondrakian_notification_scopes_effect = yes }
 option = {
  name = CAUC.0151.a
  trigger = { scope:CAUC_tondrakian_news_stage = 141 }
  remove_character_flag = CAUC_tondrakian_rejected_testimony
  add_character_flag = { flag = CAUC_tondrakian_follow_testimony years = 2 }
  ai_chance = { base = 25 }
 }
 option = {
  name = CAUC.0151.b
  trigger = { scope:CAUC_tondrakian_news_stage = 141 }
  remove_character_flag = CAUC_tondrakian_follow_testimony
  add_character_flag = { flag = CAUC_tondrakian_rejected_testimony years = 2 }
  add_piety = 100
  ai_chance = { base = 75 }
 }
 option = {
  name = CAUC.0151.land_a
  trigger = { scope:CAUC_tondrakian_news_stage = 142 has_character_flag = CAUC_tondrakian_follow_testimony }
  add_learning_lifestyle_xp = 75
  add_piety = -25
  ai_chance = { base = 50 }
 }
 option = {
  name = CAUC.0151.land_b
  trigger = { scope:CAUC_tondrakian_news_stage = 142 has_character_flag = CAUC_tondrakian_follow_testimony }
  add_piety = 50
  ai_chance = { base = 50 }
 }
 option = {
  name = CAUC.0151.prohibition_a
  trigger = { scope:CAUC_tondrakian_news_stage = 143 has_character_flag = CAUC_tondrakian_follow_testimony }
  add_piety = -50
  add_prestige = 50
  ai_chance = { base = 35 }
 }
 option = {
  name = CAUC.0151.prohibition_b
  trigger = { scope:CAUC_tondrakian_news_stage = 143 has_character_flag = CAUC_tondrakian_follow_testimony }
  remove_character_flag = CAUC_tondrakian_follow_testimony
  add_character_flag = { flag = CAUC_tondrakian_rejected_testimony years = 2 }
  add_piety = 100
  ai_chance = { base = 65 }
 }
 option = {
  name = CAUC.0151.result
  trigger = { scope:CAUC_tondrakian_news_stage = 144 }
  remove_character_flag = CAUC_tondrakian_follow_testimony
  remove_character_flag = CAUC_tondrakian_rejected_testimony
  ai_chance = { base = 100 }
 }
 '''+join.replace('trigger = { '+gate+' }','trigger = { '+gate+' scope:CAUC_tondrakian_news_stage >= 143 }')+'\n}')
 # An absent Christian local host must not silence the regional storyline.
 # Faith-scope scheduling survives a county-holder death. A real investigation
 # takes over the testimony broadcasts as soon as its first scene opens.
 for i in range(4):
  event=152+i;stage=141+i
  follow=f'trigger_event = {{ id = CAUC.{event+1:04d} days = 60 }}' if i<3 else ''
  events.append(f'''CAUC.{event:04d} = {{ hidden = yes scope = faith
   trigger = {{ exists = global_var:CAUC_tondrakian_founder NOT = {{ has_global_variable = CAUC_tondrakian_inquiry_started }} }}
   immediate = {{ save_scope_value_as = {{ name = CAUC_tondrakian_news_stage value = {stage} }} CAUC_tondrakian_broadcast_followup_effect = yes {follow} }}
  }}''')

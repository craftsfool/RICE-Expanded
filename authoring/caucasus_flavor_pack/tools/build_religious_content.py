#!/usr/bin/env python3
"""Build five optional regional stories and matching English, Chinese and French text."""
import json
from pathlib import Path
from ck3_script import write, entries, canonical

ROOT = Path(__file__).resolve().parents[1]
LANGS = ('english', 'simp_chinese', 'french')
LOC = {lang: {} for lang in LANGS}
EVENTS, DECISIONS, MODIFIERS, FLOWS = [], [], [], []

def loc(key, en, zh, fr):
 for lang, value in zip(LANGS, (en, zh, fr)):
  assert key not in LOC[lang], key
  LOC[lang][key] = value
 return key

def option(key, words, effect, condition='', weight=50):
 loc(key, *words)
 gate = 'trigger = { ' + condition + ' }' if condition else ''
 return 'option = { name = ' + key + ' ' + gate + ' ' + effect + ' ai_chance = { base = ' + str(weight) + ' } }'

def event(number, title, desc, county, opts, immediate='', theme='learning', extra=''):
 key = 'CAUC.' + str(number).zfill(4)
 portrait = ''
 if 140 <= number <= 144:
  immediate = 'CAUC_tondrakian_recover_speaker_effect = yes ' + immediate
  portrait = '\n right_portrait = { character = scope:CAUC_tondrakian_speaker }\n'
  intro = ('[CAUC_tondrakian_speaker.GetFullName] speaks for the assemblies. ', '[CAUC_tondrakian_speaker.GetFullName]为聚会众人发言。', '[CAUC_tondrakian_speaker.GetFullName] parle au nom des assemblées. ')
  desc = tuple(prefix + value for prefix,value in zip(intro,desc))
 loc(key+'.t', *title); loc(key+'.desc', *desc)
 body = '\n'.join(option(key+'.'+chr(97+i), *opt) for i, opt in enumerate(opts))
 EVENTS.append(key+' = {\n type = character_event\n title = '+key+'.t\n desc = '+key+'.desc\n theme = '+theme+'\n left_portrait = { character = root }\n'+portrait+' trigger = { is_landed = yes is_available_adult = yes is_imprisoned = no has_title = title:'+county+' '+extra+' }\n'+(' immediate = { '+immediate+' }\n' if immediate else '')+body+'\n}\n')
 return key

def follow(number, days=60):
 return 'trigger_event = { id = CAUC.'+str(number).zfill(4)+' days = '+str(days)+' }'

def county_effect(county, effect):
 return 'title:'+county+' = { '+effect+' }'

def clear_policy(county, names):
 return county_effect(county, ' '.join('remove_county_modifier = '+name for name in names))

def policy(county, name, years=5):
 return county_effect(county, 'add_county_modifier = { modifier = '+name+' years = '+str(years)+' }')

def state(county, flow, value):
 return county_effect(county, 'set_variable = { name = CAUC_'+flow+'_choice value = '+str(value)+' }')

def end(flow):
 return 'remove_character_flag = CAUC_'+flow+'_active'

def modifier(name, title, desc, mechanics):
 loc(name, *title); loc(name+'_desc', *desc)
 MODIFIERS.append(name+' = { '+mechanics+' }\n')

def decision(flow, county, name, desc, tip, context, first_event, cost=25, shown='', setup='', terminal_mods=()):
 key = 'CAUC_'+flow+'_decision'
 loc(key, *name); loc(key+'_desc', *desc); loc(key+'_tooltip', *tip); loc(key+'_context', *context)
 loc(key+'_confirm', 'Convene the meeting', '召集众人', 'Réunir les parties')
 valid = 'NOT = { has_character_flag = CAUC_'+flow+'_active }'
 for mod in terminal_mods:
  valid += ' NOT = { title:'+county+' = { has_county_modifier = '+mod+' } }'
 effect = 'add_character_flag = { flag = CAUC_'+flow+'_active years = 1 } '+setup+' if = { limit = { has_game_rule = RICE_historical_context_on } custom_tooltip = '+key+'_context } '+follow(first_event, 1)
 picture = 'CAUC_derbent_pass.dds' if county=='c_derbent' else 'decision_castle_view.dds'
 DECISIONS.append(key+' = {\n picture = { reference = "gfx/interface/illustrations/decisions/'+picture+'" }\n decision_group_type = RICE_regional\n desc = '+key+'_desc\n selection_tooltip = '+key+'_tooltip\n confirm_text = '+key+'_confirm\n ai_check_interval_by_tier = { barony = 0 county = 48 duchy = 48 kingdom = 64 empire = 64 hegemony = 64 }\n cooldown = { years = 10 }\n is_shown = { is_landed = yes has_title = title:'+county+' '+shown+' }\n is_valid = { '+valid+' }\n is_valid_showing_failures_only = { is_available_adult = yes is_imprisoned = no is_at_war = no }\n cost = { gold = '+str(cost)+' }\n effect = { '+effect+' }\n ai_potential = { short_term_gold >= '+str(cost*3)+' }\n ai_will_do = { base = 10 }\n}\n')
 FLOWS.append({'flow':flow,'decision':key,'county':county,'start_event':'CAUC.'+str(first_event).zfill(4),'cost':cost,'policy_modifiers':list(terminal_mods),'cooldown_years':10,'active_flag_expires_years':1})

CHRISTIAN = 'faith = { religion = religion:christianity_religion }'
MUSLIM = 'faith = { religion = religion:islam_religion }'

# DERBENT: a foreign retinue, religious pressure, then a settlement.
derbent_mods = ('CAUC_rus_protected', 'CAUC_rus_instructed', 'CAUC_rus_dismissed')
decision('derbent_guards','c_derbent',
 ('Recruit Rus Guards at $c_derbent$','在$c_derbent$招募罗斯近卫','Recruter une garde rus’ à $c_derbent$'),
 ('A Rus retinue offers its service at the gate. Their captain promises loyalty, but the town’s preachers object to placing men of another religion beside my household. I will hear both sides before settling the guards’ position.','一队罗斯战士来到城门前，愿意为我效力。队长承诺忠诚，城里的传教士却反对让异教徒守在我身旁。我将听取双方的意见，再决定近卫的地位。','Une troupe rus’ propose ses services à la porte. Son capitaine promet sa fidélité, mais les prédicateurs de la ville s’opposent à ce que des hommes d’une autre religion gardent ma maisonnée. J’entendrai les deux parties avant de fixer la place de ces gardes.'),
 ('Recruit a retinue and resolve religious objections in a three-stage story. The final policy lasts five years.','招募近卫，并通过三阶段事件处理宗教争端。最终政策持续五年。','Recruter une troupe et régler les objections religieuses dans un récit en trois étapes. La politique finale dure cinq ans.'),
 ('In 989–990, the preacher Musa al-Tusi demanded that Maymun of Derbent surrender his Rus guards for conversion or death. Maymun refused; a siege and his departure followed. This story adapts the dispute without recreating its participants.','989—990年，传教士穆萨·图西要求杰尔宾特的迈蒙交出罗斯近卫，让他们改信，否则处死。迈蒙拒绝，随后遭到围城，并带着近卫离开。本事件改编这一争端，不重现当时的人物。','En 989–990, le prédicateur Musa al-Tusi exigea que Maymun de Derbent livre ses gardes rus’ pour qu’ils se convertissent ou soient mis à mort. Maymun refusa ; un siège et son départ suivirent. Ce récit adapte le différend sans recréer ses protagonistes.'),
 100,75,MUSLIM+' current_date < 1200.1.1',terminal_mods=derbent_mods)
event(100,('An Oath at the Gate','城门前的誓言','Un serment à la porte'),
 ('The Rus captain offers an oath of service. His men will answer to my officers and receive their pay from my treasury. A preacher asks whether that oath can bind men who do not share our worship. I have promised a hearing before anyone makes demands of the retinue.','罗斯队长宣誓效忠。他的人将听从我的军官调遣，由我的府库支付军饷。一位传教士问，不与我们同奉一种信仰的人，如何受这一誓言约束。我答应先举行听证，再对近卫提出要求。','Le capitaine rus’ prête serment de service. Ses hommes obéiront à mes officiers et recevront leur solde de mon trésor. Un prédicateur demande si ce serment peut lier des hommes qui ne partagent pas notre culte. J’ai promis de les entendre avant toute exigence envers la troupe.'),
 'c_derbent',[(('Record the oath and summon the preacher.','记下誓言，召来传教士。','Consigner le serment et convoquer le prédicateur.'),follow(101,30))],theme='martial',extra=MUSLIM)
event(101,('The Preacher’s Demand','传教士的要求','L’exigence du prédicateur'),
 ('The preacher calls for the guards to receive instruction and accept our faith. The captain answers that his men came to serve, not to surrender their beliefs. Town elders warn that this quarrel is drawing crowds. I must decide whose assurance will carry my authority.','传教士要求近卫接受教导，改信我们的宗教。队长回答，他们是来效力的，不是来放弃自身信仰的。城中长老提醒我，争执已经引来围观的人群。我必须决定，以自己的权威保障哪一方的承诺。','Le prédicateur exige que les gardes soient instruits et adoptent notre foi. Le capitaine répond que ses hommes sont venus servir, non abandonner leurs croyances. Les anciens de la ville avertissent que la querelle attire une foule. Je dois décider quel engagement sera garanti par mon autorité.'),
 'c_derbent',[
 (('Their service earns my protection.','他们的效忠值得我的保护。','Leur service leur vaut ma protection.'),clear_policy('c_derbent',derbent_mods)+policy('c_derbent',derbent_mods[0])+state('c_derbent','derbent_guards',1)+' add_piety = -75 '+follow(102)),
 (('Offer instruction and wages to those who accept it.','提供教导，并向愿意接受的人支付军饷。','Offrir une instruction et une solde à ceux qui l’acceptent.'),clear_policy('c_derbent',derbent_mods)+policy('c_derbent',derbent_mods[1])+state('c_derbent','derbent_guards',2)+' add_piety = 50 '+follow(102)),
 (('Pay their departure and dismiss the retinue.','付清遣散费，让近卫离开。','Payer leur départ et congédier la troupe.'),clear_policy('c_derbent',derbent_mods)+policy('c_derbent',derbent_mods[2])+state('c_derbent','derbent_guards',3)+' remove_short_term_gold = 25 add_piety = 75 '+follow(102),'gold >= 25')
 ],theme='diplomacy',extra=MUSLIM)
event(102,('The Town’s Answer','城里的回应','La réponse de la ville'),
 ('The elders bring petitions about my decision. Some praise a clear settlement; others demand that I reconsider. My officers ask for money to keep the watch supplied while the town adjusts. I can pay for that reassurance or require them to work with the arrangements already made.','长老们带来了有关我决定的请愿。有的赞成明确处置，有的要求我重新考虑。军官们请求拨款，在城里适应新安排的期间保障值守。我可以花钱稳住局面，也可以让他们照现有安排办事。','Les anciens apportent des requêtes au sujet de ma décision. Certains saluent un règlement clair ; d’autres demandent que je le revoie. Mes officiers réclament des fonds pour ravitailler la garde pendant que la ville s’adapte. Je peux financer cette assurance ou leur demander de respecter les arrangements déjà pris.'),
 'c_derbent',[
 (('Provide the money and confirm the settlement.','拨款，并确认处置。','Fournir les fonds et confirmer le règlement.'),'remove_short_term_gold = 25 '+county_effect('c_derbent','change_county_control = 8')+' '+end('derbent_guards'),'gold >= 25'),
 (('The settlement stands; there will be no further grant.','处置照旧，不再增拨款项。','Le règlement tient ; il n’y aura pas de nouveau don.'),county_effect('c_derbent','change_county_control = -5')+' '+end('derbent_guards'))
 ],theme='stewardship',extra=MUSLIM)
modifier('CAUC_rus_protected',('Protected Rus Retinue','受保护的罗斯近卫','Troupe rus’ protégée'),('The ruler protects foreign guards despite local religious objections.','统治者不顾当地宗教人士的反对，保护异教近卫。','Le dirigeant protège les gardes étrangers malgré les objections religieuses locales.'),'levy_size = 0.10 county_opinion_add = -10')
modifier('CAUC_rus_instructed',('Instruction for the Retinue','近卫的宗教教导','Instruction de la troupe'),('Religious instruction and new service terms retain part of the foreign retinue.','宗教教导与新的效力条件使部分外来近卫留下。','Une instruction religieuse et de nouvelles conditions de service retiennent une partie de la troupe étrangère.'),'levy_size = 0.05 tax_mult = -0.03')
modifier('CAUC_rus_dismissed',('Dismissed Foreign Guards','外来近卫遣散','Gardes étrangers congédiés'),('The retinue has departed; local religious leaders welcome the decision.','近卫已经离开；当地宗教领袖欢迎这一决定。','La troupe est partie ; les autorités religieuses locales saluent la décision.'),'levy_size = -0.05 county_opinion_add = 8')

# LORI: monastic autonomy, ecclesiastical rapprochement and the cost of agreement.
lori_mods = ('CAUC_lori_autonomy','CAUC_lori_rapprochement','CAUC_lori_guarantees')
decision('lori_council','c_lori',
 ('Hear the Churches of $c_lori$','听取$c_lori$教会的争论','Entendre les Églises de $c_lori$'),
 ('The monasteries disagree over proposals for closer relations with neighboring churches. Some fear that agreement will cost them their liturgy and authority over their houses. I can host a discussion and decide what protection or support to offer.','修道院对与邻近教会加强联系的提议意见不一。有些人担心，和解会使他们失去自身礼仪与修道院的自主权。我可以主持讨论，决定给予何种保障或资助。','Les monastères ne s’accordent pas sur les propositions de rapprochement avec les Églises voisines. Certains craignent d’y perdre leur liturgie et l’autorité sur leurs maisons. Je peux accueillir une discussion et décider des garanties ou du soutien à offrir.'),
 ('Choose between monastic autonomy, ecclesiastical dialogue and guarantees for both sides. A three-stage discussion produces a five-year policy.','在修道院自主、教会对话与双方保障之间作出选择。三阶段讨论将形成持续五年的政策。','Choisir entre l’autonomie monastique, le dialogue ecclésiastique et des garanties pour les deux parties. Une discussion en trois étapes aboutit à une politique de cinq ans.'),
 ('During the Armenian–Byzantine union negotiations of the 1170s, the leaders of Sanahin and Haghpat opposed concessions and did not attend the Hromkla council, dated to 1178 or 1179. This local dispute is a fictional adaptation, not the council itself.','1170年代亚美尼亚与拜占庭商议教会合一时，萨纳欣与哈格帕特的领袖反对妥协，并缺席赫罗姆克拉会议；该会议有1178或1179年两种定年。本地争论是游戏改编，不是会议本身。','Lors des négociations d’union arméno-byzantines des années 1170, les responsables de Sanahin et de Haghpat s’opposèrent aux concessions et n’assistèrent pas au concile de Hromkla, daté de 1178 ou 1179. Ce différend local est une adaptation fictive, non le concile lui-même.'),
 110,25,CHRISTIAN+' current_date >= 1100.1.1',terminal_mods=lori_mods)
event(110,('The Abbots’ Conditions','院长们的条件','Les conditions des abbés'),
 ('The abbots will discuss reconciliation, but they ask me to promise that no agreement will be imposed before they have examined it. An envoy argues that delay will offend the neighboring church. I can protect the monasteries’ independence, support closer relations, or require guarantees before either side proceeds.','院长们愿意讨论和解，但请求我承诺：在他们审议之前，不强行推行任何协议。使者则说，拖延会冒犯邻近教会。我可以保护修道院的自主，支持加强联系，或要求双方先作出保障。','Les abbés acceptent de discuter d’un rapprochement, mais demandent qu’aucun accord ne leur soit imposé avant leur examen. Un envoyé affirme que tout retard offensera l’Église voisine. Je peux protéger l’indépendance des monastères, soutenir le rapprochement ou exiger des garanties avant de poursuivre.'),
 'c_lori',[
 (('Their houses will judge their own liturgy.','让各修道院自行审议本身的礼仪。','Leurs maisons jugeront elles-mêmes de leur liturgie.'),clear_policy('c_lori',lori_mods)+policy('c_lori',lori_mods[0])+state('c_lori','lori_council',1)+' add_piety = 50 '+follow(111)),
 (('Fund the dialogue and the translation of its proposals.','资助对话，并翻译各项提议。','Financer le dialogue et la traduction des propositions.'),clear_policy('c_lori',lori_mods)+policy('c_lori',lori_mods[1])+state('c_lori','lori_council',2)+' add_learning_lifestyle_xp = 100 '+follow(111)),
 (('Guarantee local rites before discussing agreement.','先保障当地礼仪，再商议协议。','Garantir les rites locaux avant de discuter d’un accord.'),clear_policy('c_lori',lori_mods)+policy('c_lori',lori_mods[2])+state('c_lori','lori_council',3)+' remove_short_term_gold = 25 '+follow(111),'gold >= 25')
 ],extra=CHRISTIAN)
event(111,('Words in the Margin','页边的批注','Des mots dans la marge'),
 ('A translated proposal has reached the copyists. One reader says its wording preserves local practice; another finds a concession concealed in the margin. The abbots ask for a second translation before they continue. The work will take funds and time.','一份译出的提议送到了抄写员手中。一位读者认为，措辞保留了当地习惯；另一位却从页边批注中发现了隐藏的妥协。院长们请求再作一份译文，然后继续讨论。这需要时间，也需要钱。','Une proposition traduite est parvenue aux copistes. Un lecteur estime qu’elle préserve les usages locaux ; un autre trouve une concession dissimulée dans la marge. Les abbés demandent une seconde traduction avant de poursuivre. Ce travail exigera des fonds et du temps.'),
 'c_lori',[
 (('Pay for a second reading.','出钱，请他们重新审读。','Payer une seconde lecture.'),'remove_short_term_gold = 20 add_learning_lifestyle_xp = 75 '+follow(112),'gold >= 20'),
 (('Suspend this proposal and keep the existing safeguards.','搁置这项提议，保留现有保障。','Suspendre cette proposition et maintenir les garanties.'),'add_prestige = -25 '+follow(112))
 ],extra=CHRISTIAN)
event(112,('A Record of the Discussion','讨论的记录','Le compte rendu de la discussion'),
 ('The discussion has ended without bringing the churches into a single institution. The copyists have recorded the arguments, while my promises to the monasteries remain in force. They ask whether I will pay to circulate the record or leave it in their own libraries.','讨论结束了，教会并未合并成一个机构。抄写员记下了各方论据，我向修道院作出的承诺也仍然有效。他们问，我是否愿意出钱传抄这份记录，还是只将它留在各院的藏书中。','La discussion s’est achevée sans réunir les Églises en une seule institution. Les copistes ont consigné les arguments et mes promesses aux monastères restent en vigueur. Ils me demandent si je financerai la diffusion du compte rendu ou le laisserai dans leurs bibliothèques.'),
 'c_lori',[
 (('Let other scholars read what was said.','让其他学者也读到这些讨论。','Que d’autres savants puissent lire ces échanges.'),'remove_short_term_gold = 15 add_learning_lifestyle_xp = 100 '+end('lori_council'),'gold >= 15'),
 (('Keep the record in the monasteries.','将记录留在修道院。','Conserver le compte rendu dans les monastères.'),'add_piety = 25 '+end('lori_council'))
 ],extra=CHRISTIAN)
modifier('CAUC_lori_autonomy',('Monastic Autonomy','修道院自主','Autonomie monastique'),('Local monasteries retain authority over their liturgy and houses.','当地修道院保有自身礼仪与院务的自主权。','Les monastères locaux conservent l’autorité sur leur liturgie et leurs maisons.'),'county_opinion_add = 10 tax_mult = -0.03')
modifier('CAUC_lori_rapprochement',('Ecclesiastical Dialogue','教会对话','Dialogue ecclésiastique'),('Translations and discussions encourage learning, but local opponents distrust the proposals.','翻译与讨论促进学术，但当地反对者仍不信任这些提议。','Les traductions et les discussions favorisent les études, mais les opposants locaux se méfient des propositions.'),'development_growth_factor = 0.08 county_opinion_add = -5')
modifier('CAUC_lori_guarantees',('Guaranteed Local Rites','当地礼仪保障','Rites locaux garantis'),('A funded agreement safeguards local practice while allowing dialogue.','有经费支持的协议保障当地习俗，同时允许开展对话。','Un accord financé protège les usages locaux tout en permettant le dialogue.'),'county_opinion_add = 5 development_growth_factor = 0.03')

# ANI: building use is persistent; it is never a county conversion.
ani_mods = ('CAUC_ani_church_restored','CAUC_ani_mosque_endowed','CAUC_ani_existing_use')
ani_setup = county_effect('c_hayk', 'if = { limit = { NOT = { has_variable = CAUC_ani_sanctuary_use } } if = { limit = { root = { current_date >= 1064.1.1 current_date < 1124.1.1 } } set_variable = { name = CAUC_ani_sanctuary_use value = 2 } } else = { set_variable = { name = CAUC_ani_sanctuary_use value = 1 } } }')
decision('ani_sanctuary','c_hayk',
 ('Settle the Use of Ani’s Cathedral','裁定阿尼主教座堂的用途','Régler l’usage de la cathédrale d’Ani'),
 ('The cathedral has changed hands, and its present congregation fears another change. Petitioners bring deeds, memories and claims of conquest. I can settle the building’s use and decide what protection its displaced congregation will receive.','主教座堂曾易手，如今的会众害怕它再次改换用途。请愿者带来了契据、往事和征服所得的主张。我将裁定这座建筑的用途，并决定如何安置被迫离开的会众。','La cathédrale a changé de mains et sa communauté actuelle redoute un nouveau changement. Les requérants apportent des actes, des souvenirs et des droits issus de la conquête. Je peux fixer l’usage du bâtiment et décider de la protection accordée à la communauté déplacée.'),
 ('Record the sanctuary’s use, settle rival claims and protect another place of worship. The county’s faith will not change.','记录圣所用途，裁定双方主张，并保障另一处礼拜场所。此事不会改变全县信仰。','Consigner l’usage du sanctuaire, régler les revendications et protéger un autre lieu de culte. La foi du comté restera inchangée.'),
 ('Ani’s cathedral became a mosque following the conquest of 1064 and returned to church use in 1124. The initial use follows those dates; subsequent choices persist in this save. The petitions and settlement are fictional.','阿尼主教座堂在1064年被征服后改作清真寺，1124年恢复教堂用途。初始用途参照这两个年代，此后保存玩家的决定。请愿与裁决情节为游戏创作。','La cathédrale d’Ani fut transformée en mosquée après la conquête de 1064, puis rendue au culte chrétien en 1124. Son usage initial suit ces dates ; les choix ultérieurs restent enregistrés dans cette partie. Les requêtes et le règlement sont fictifs.'),
 120,25,'OR = { '+CHRISTIAN+' '+MUSLIM+' } current_date >= 1064.1.1',setup=ani_setup,terminal_mods=ani_mods)
loc('CAUC_ani_church_use','The cathedral is recorded as a church.','主教座堂现记为教堂。','La cathédrale est enregistrée comme église.')
loc('CAUC_ani_mosque_use','The cathedral is recorded as a mosque.','主教座堂现记为清真寺。','La cathédrale est enregistrée comme mosquée.')
ani_show = 'if = { limit = { title:c_hayk = { var:CAUC_ani_sanctuary_use = 1 } } custom_tooltip = CAUC_ani_church_use } else = { custom_tooltip = CAUC_ani_mosque_use }'
event(120,('One Building, Two Claims','一座建筑，两方主张','Un bâtiment, deux revendications'),
 ('The petitioners spread their documents before me. One community recalls the cathedral’s dedication; the other points to the rights granted after the conquest. A change of use will require repairs and a new endowment. Whatever I decide, the displaced congregation asks for a place where it can worship without interference.','请愿者在我面前摊开文书。一方追溯主教座堂的祝圣，另一方援引征服后授予的权利。改换用途需要修缮与新的捐产。无论如何裁定，被迫离开的会众都请求一处不受干扰的礼拜场所。','Les requérants étalent leurs documents devant moi. Une communauté rappelle la consécration de la cathédrale ; l’autre invoque les droits accordés après la conquête. Un changement d’usage exigera des réparations et une nouvelle dotation. Quelle que soit ma décision, la communauté déplacée demande un lieu où pratiquer son culte sans entrave.'),
 'c_hayk',[
 (('Restore the cathedral to Christian worship.','恢复主教座堂的基督教礼拜。','Rendre la cathédrale au culte chrétien.'),clear_policy('c_hayk',ani_mods)+policy('c_hayk',ani_mods[0])+county_effect('c_hayk','set_variable = { name = CAUC_ani_sanctuary_use value = 1 }')+' remove_short_term_gold = 50 add_piety = 50 '+follow(121),'gold >= 50 '+CHRISTIAN),
 (('Endow it as a mosque.','为清真寺用途拨付捐产。','Doter le bâtiment en tant que mosquée.'),clear_policy('c_hayk',ani_mods)+policy('c_hayk',ani_mods[1])+county_effect('c_hayk','set_variable = { name = CAUC_ani_sanctuary_use value = 2 }')+' remove_short_term_gold = 50 add_piety = 50 '+follow(121),'gold >= 50 '+MUSLIM),
 (('Confirm its present use and protect other worship.','确认现有用途，保障其他社群礼拜。','Confirmer son usage actuel et protéger les autres cultes.'),clear_policy('c_hayk',ani_mods)+policy('c_hayk',ani_mods[2])+ani_show+' add_piety = -25 '+follow(121))
 ],immediate=ani_show,theme='diplomacy',extra='OR = { '+CHRISTIAN+' '+MUSLIM+' }')
event(121,('The Keys and the Deeds','钥匙与契据','Les clefs et les actes'),
 ('The building’s use has been entered in the register. Now the clerks must settle its endowment and identify another place for the congregation whose claim was refused. The petitioners disagree over rents and access. A survey would cost money; enforcing the existing deeds would be quicker, but less welcome.','建筑用途已经入册。如今，书记们还要划定捐产，为诉求未获准的会众安排另一处礼拜场所。请愿者又对租金与出入权发生争执。勘查需要花钱；直接依旧契执行更快，却难免招怨。','L’usage du bâtiment a été inscrit au registre. Les clercs doivent désormais régler sa dotation et trouver un autre lieu pour la communauté dont la revendication a été rejetée. Les requérants disputent les loyers et les accès. Une enquête coûterait de l’argent ; faire appliquer les actes existants serait plus rapide, mais moins bien accueilli.'),
 'c_hayk',[
 (('Pay the surveyors to mark the boundaries.','出钱请测量员厘清界址。','Payer les arpenteurs pour établir les limites.'),'remove_short_term_gold = 20 '+county_effect('c_hayk','change_county_control = 5')+' '+follow(122),'gold >= 20'),
 (('Enforce the deeds already held.','依现有契据执行。','Faire appliquer les actes existants.'),county_effect('c_hayk','change_county_control = -3')+' '+follow(122))
 ],theme='stewardship')
event(122,('A Place to Pray','礼拜之所','Un lieu pour prier'),
 ('Both communities have received copies of my judgment. The cathedral’s assigned use remains recorded, and the other congregation has been promised protection for its own place of worship. The clerks ask whether I will fund repairs there or leave their upkeep to the worshippers.','两个社群都收到了裁决副本。主教座堂的用途继续记在册中，另一方的礼拜场所也得到了保护承诺。书记们问，我是否愿意资助那里的修缮，还是交给会众自行维护。','Les deux communautés ont reçu une copie de mon jugement. L’usage attribué à la cathédrale reste enregistré, et l’autre communauté bénéficie d’une promesse de protection pour son propre lieu de culte. Les clercs me demandent si je financerai les réparations ou en laisserai l’entretien aux fidèles.'),
 'c_hayk',[
 (('Provide a grant for the other congregation.','向另一方会众拨付修缮款。','Accorder un don à l’autre communauté.'),'remove_short_term_gold = 25 add_prestige = 50 '+county_effect('c_hayk','change_county_control = 5')+' '+end('ani_sanctuary'),'gold >= 25'),
 (('Their protection is assured; they must maintain it.','保护已有保障，维护由他们负责。','Leur protection est garantie ; ils assureront l’entretien.'),'add_prestige = 15 '+end('ani_sanctuary'))
 ],theme='diplomacy')
modifier(ani_mods[0],('Restored Cathedral','恢复礼拜的主教座堂','Cathédrale restaurée'),('The cathedral has been restored to Christian worship, despite rival claims.','主教座堂已恢复基督教礼拜，但仍有另一方的权利争议。','La cathédrale a été rendue au culte chrétien malgré les revendications concurrentes.'),'county_opinion_add = -5 development_growth_factor = 0.05')
modifier(ani_mods[1],('Endowed Mosque','获拨捐产的清真寺','Mosquée dotée'),('An endowment supports the mosque, despite rival claims to the building.','捐产支持清真寺运作，但建筑仍有另一方的权利争议。','Une dotation soutient la mosquée malgré les revendications concurrentes sur le bâtiment.'),'county_opinion_add = -5 tax_mult = 0.05')
modifier(ani_mods[2],('Protected Places of Worship','礼拜场所保障','Lieux de culte protégés'),('The sanctuary retains its present use and other congregations receive protection.','圣所维持现有用途，其他会众也得到保护。','Le sanctuaire conserve son usage actuel et les autres communautés bénéficient d’une protection.'),'county_opinion_add = 8 tax_mult = -0.03')

# ALANIA: missionary pressure and local sanctuaries, without a fabricated pantheon.
alan_mods = ('CAUC_alan_mission_supported','CAUC_alan_old_rites_protected','CAUC_alan_mission_dismissed')
decision('alan_mission','c_maghas',
 ('Receive Missionaries in Alania','接见阿兰传教士','Recevoir des missionnaires en Alanie'),
 ('Christian envoys ask for land and safe passage. Local elders fear for the sanctuaries where their families have long gathered. I will hear the envoys and decide whether their mission should receive support, limits or an order to leave.','基督教使者请求土地与通行保障。当地长老担心，他们家族世代聚会的圣所将受威胁。我将接见使者，决定资助传教、划定界限，还是令其离开。','Des envoyés chrétiens demandent des terres et un passage sûr. Les anciens craignent pour les sanctuaires où leurs familles se réunissent depuis longtemps. J’entendrai les envoyés et déciderai de soutenir leur mission, de la limiter ou de leur ordonner de partir.'),
 ('Resolve a three-stage dispute over missionaries and local rites. The policy lasts five years; no mass conversion is imposed.','通过三阶段争论处理传教与地方仪式的关系。政策持续五年，不强制全县改宗。','Régler un différend en trois étapes entre les missionnaires et les rites locaux. La politique dure cinq ans, sans conversion collective imposée.'),
 ('Al-Masudi reported an expulsion of Christian clergy from Alania in 932. The extent of that reversal remains uncertain, and conversion proceeded gradually. This story uses local sanctuaries without projecting modern Ossetian divine names back into the ninth century.','马苏第记载，932年阿兰驱逐了基督教教士。这一反弹的范围仍不明确，改宗也并非一蹴而就。本事件使用地方圣所的叙事，不将近现代奥塞梯的神名直接倒推至九世纪。','Al-Masudi rapporte l’expulsion de clercs chrétiens d’Alanie en 932. L’ampleur de ce recul reste incertaine et la conversion fut progressive. Ce récit évoque les sanctuaires locaux sans projeter les noms divins de l’Ossétie moderne dans le IXe siècle.'),
 130,25,'current_date < 1200.1.1',terminal_mods=alan_mods)
event(130,('The Mission’s Request','传教使团的请求','La demande de la mission'),
 ('The envoys bring books and request a house from which to teach. An elder answers that families already keep their own gathering places and oaths. He fears that a new church will claim both land and the right to forbid those rites. I must give the envoys a clear answer.','使者带来了书籍，请求一处房舍用于教导。长老回答，各家族早已有自己的聚会场所与誓约。他担心，新教堂既要占地，也要禁止这些仪式。我必须给使者明确答复。','Les envoyés apportent des livres et demandent une maison pour enseigner. Un ancien répond que les familles possèdent déjà leurs lieux de réunion et leurs serments. Il craint qu’une nouvelle église ne réclame des terres et le droit d’interdire ces rites. Je dois donner une réponse claire aux envoyés.'),
 'c_maghas',[
 (('Provide land and shelter for their teaching.','提供土地与房舍，支持教导。','Fournir des terres et un abri pour leur enseignement.'),clear_policy('c_maghas',alan_mods)+policy('c_maghas',alan_mods[0])+state('c_maghas','alan_mission',1)+' remove_short_term_gold = 25 add_learning_lifestyle_xp = 100 '+follow(131),'gold >= 25'),
 (('They may teach, but local sanctuaries are protected.','允许教导，但须保障地方圣所。','Ils peuvent enseigner, mais les sanctuaires locaux sont protégés.'),clear_policy('c_maghas',alan_mods)+policy('c_maghas',alan_mods[1])+state('c_maghas','alan_mission',2)+' add_prestige = 25 '+follow(131)),
 (('Escort the missionaries out of my lands.','护送传教士离开我的领地。','Escorter les missionnaires hors de mes terres.'),clear_policy('c_maghas',alan_mods)+policy('c_maghas',alan_mods[2])+state('c_maghas','alan_mission',3)+' add_prestige = -25 '+follow(131))
 ],theme='diplomacy')
event(131,('An Oath at the Sanctuary','圣所前的誓约','Un serment au sanctuaire'),
 ('A quarrel has broken out over a gathering at a local sanctuary. The elders demand that their oaths be respected. Supporters of the mission question whether such gatherings can coexist with Christian teaching. My officers ask for a public hearing before the dispute becomes a feud.','地方圣所的一次聚会引发了争执。长老要求尊重他们的誓约，传教的支持者则怀疑，这样的聚会是否能与基督教教导并存。军官们请求公开听证，免得争论演变成家族仇杀。','Une querelle a éclaté à propos d’une réunion dans un sanctuaire local. Les anciens exigent le respect de leurs serments. Les partisans de la mission doutent que ces assemblées puissent coexister avec l’enseignement chrétien. Mes officiers demandent une audience publique avant que le différend ne devienne une vendetta.'),
 'c_maghas',[
 (('Pay for a hearing and record its limits.','资助听证，记下双方的界限。','Financer une audience et en consigner les limites.'),'remove_short_term_gold = 20 '+county_effect('c_maghas','change_county_control = 6')+' '+follow(132),'gold >= 20'),
 (('My earlier decision is sufficient.','依我先前的决定处置。','Ma décision précédente suffit.'),county_effect('c_maghas','change_county_control = -4')+' '+follow(132))
 ],theme='stewardship')
event(132,('What the Families Remember','家族记得的事','Ce que les familles retiennent'),
 ('The elders and the mission’s supporters have received my terms. Neither has forgotten the quarrel. A clerk offers to keep a record of the local agreements, so that another petition need not begin with disputed memories. I can sponsor his work or leave each family to preserve its own account.','长老与传教的支持者都收到了我的条款，但双方并未忘记争执。书记愿意记下各项地方约定，免得下次请愿又从众说纷纭的往事谈起。我可以资助他，也可以让各家族保留自己的说法。','Les anciens et les partisans de la mission ont reçu mes conditions. Aucun n’a oublié la querelle. Un clerc propose de consigner les accords locaux afin qu’une autre requête ne commence pas par des souvenirs contestés. Je peux financer son travail ou laisser chaque famille conserver son récit.'),
 'c_maghas',[
 (('Record the agreements in writing.','以文书保存约定。','Consigner les accords par écrit.'),'remove_short_term_gold = 15 add_learning_lifestyle_xp = 75 '+end('alan_mission'),'gold >= 15'),
 (('Their witnesses will keep the memory.','由各自的见证人记住约定。','Leurs témoins en garderont le souvenir.'),'add_prestige = 15 '+end('alan_mission'))
 ])
modifier(alan_mods[0],('Supported Christian Mission','获资助的基督教传教','Mission chrétienne soutenue'),('The mission receives land and protection, while local families dispute its influence.','传教使团得到土地与保护，当地家族却对其影响存有异议。','La mission reçoit des terres et une protection, mais les familles locales contestent son influence.'),'development_growth_factor = 0.08 county_opinion_add = -8')
modifier(alan_mods[1],('Protected Local Sanctuaries','地方圣所保障','Sanctuaires locaux protégés'),('Local rites retain protection while missionaries may teach within agreed limits.','地方仪式受到保护，传教士可在约定界限内教导。','Les rites locaux restent protégés et les missionnaires peuvent enseigner dans les limites convenues.'),'county_opinion_add = 8 development_growth_factor = 0.03')
modifier(alan_mods[2],('Missionaries Sent Away','传教士被送走','Missionnaires renvoyés'),('The mission has departed, strengthening the elders’ position but ending its patronage.','使团离开后，长老的地位得到巩固，传教带来的资助也随之终止。','Le départ de la mission renforce la position des anciens, mais met fin à son soutien.'),'county_opinion_add = 12 development_growth_factor = -0.05')

# TONDRAKIANS: five stages with investigation choices and a native rite foundation.
ton_mods = ('CAUC_tondrakian_refuge','CAUC_tondrakian_suppressed','CAUC_tondrakian_assembly')
decision('tondrakian_inquiry','c_apahunik',
 ('Hear the Tondrakian Preachers','听取通德拉基派的讲道','Entendre les prédicateurs tondrakiens'),
 ('Reports from the villages speak of assemblies that reject holy images and question the clergy’s rights to rents and tithes. Churchmen demand an inquiry. I will hear the preachers, examine the property claims and decide whether to shelter, suppress or join their movement.','村庄传来消息：有人聚会反对圣像，并质疑教士收租与征收什一税的权利。教会要求调查。我将听取讲道者，查明地产争执，再决定庇护、镇压，或加入他们。','Les villages signalent des assemblées qui rejettent les images saintes et contestent les droits du clergé aux loyers et aux dîmes. Les autorités ecclésiastiques exigent une enquête. J’entendrai les prédicateurs, examinerai les revendications foncières et déciderai de les protéger, de les réprimer ou de les rejoindre.'),
 ('Begin a five-stage inquiry into Smbat Zarehavantsi’s rite. Armenian Apostolic rulers may join for 500 Piety, adopting it alongside Apahunik. Later inquiries hear a surviving follower if the founder has died.','开始对斯姆巴特·扎雷哈万齐所创礼制的五阶段调查。亚美尼亚使徒教会统治者可花费500虔诚加入，并使阿帕胡尼克改奉礼制。创立者去世后的调查由在世追随者出面。','Commencer une enquête en cinq étapes sur le rite de Smbat Zarehavantsi. Les dirigeants apostoliques arméniens peuvent le rejoindre pour 500 Piété, avec Apahunik. Les enquêtes ultérieures entendent un disciple vivant si le fondateur est mort.'),
 ('Tondrakian communities are attested in ninth- to eleventh-century Armenia. Much of the evidence comes from hostile church writers, including Grigor Magistros. The rite’s $tenet_aniconism_name$, $tenet_communal_possessions_name$, $tenet_unrelenting_faith_zandik_name$ and gender equality are a gameplay interpretation chosen for this expansion.','九至十一世纪的亚美尼亚已有通德拉基社群记录。许多材料来自反对他们的教会作者，包括格里戈尔·马吉斯特罗斯。本拓展采用$tenet_aniconism_name$、$tenet_communal_possessions_name$、$tenet_unrelenting_faith_zandik_name$与男女平等，作为此次指定的游戏建模。','Des communautés tondrakiennes sont attestées en Arménie du IXe au XIe siècle. Une grande partie des témoignages vient d’auteurs ecclésiastiques hostiles, dont Grigor Magistros. Les principes $tenet_aniconism_name$, $tenet_communal_possessions_name$ et $tenet_unrelenting_faith_zandik_name$, ainsi que l’égalité des sexes du rite, constituent une interprétation choisie pour cette extension.'),
 140,25,CHRISTIAN+' current_date < 1100.1.1',setup='CAUC_tondrakian_prepare_inquiry_effect = yes',terminal_mods=ton_mods)
event(140,('A Gathering without Images','没有圣像的聚会','Une assemblée sans images'),
 ('The visitors describe a meeting without holy images. Men and women speak in turn; no hereditary priest claims authority over them. A church envoy calls this disorder and asks me to close the assembly. Before judging, I must decide how the inquiry will be conducted.','来客描述了一场没有圣像的聚会。男女轮流发言，没有世袭教士宣称有权管辖他们。教会使者称之为乱象，要求我取缔聚会。作出裁决前，我须决定如何调查。','Les visiteurs décrivent une assemblée sans images saintes. Hommes et femmes prennent la parole à tour de rôle ; aucun prêtre héréditaire ne revendique d’autorité sur eux. Un envoyé de l’Église y voit du désordre et me demande de fermer l’assemblée. Avant de juger, je dois fixer les conditions de l’enquête.'),
 'c_apahunik',[
 (('Hear the villagers under my protection.','由我保护村民，听取他们的陈述。','Entendre les villageois sous ma protection.'),state('c_apahunik','tondrakian_inquiry',1)+' add_piety = -25 '+follow(141,30)),
 (('Let the church present its accusations first.','先让教会提出指控。','Laisser d’abord l’Église présenter ses accusations.'),state('c_apahunik','tondrakian_inquiry',2)+' add_piety = 25 '+follow(141,30)),
 (('Pay clerks to record both accounts.','出钱请书记记录双方说法。','Payer des clercs pour consigner les deux récits.'),state('c_apahunik','tondrakian_inquiry',3)+' remove_short_term_gold = 20 add_learning_lifestyle_xp = 50 '+follow(141,30),'gold >= 20')
 ],extra=CHRISTIAN)
event(141,('Whose Voice May Be Heard?','谁有权发言？','Qui a le droit de parler ?'),
 ('A woman from the assembly asks to answer the accusations herself. The envoy insists that only an ordained man may speak on matters of doctrine. The villagers reply that faith does not confer a different worth on men and women. My hearing will either admit her testimony or follow the envoy’s procedure.','聚会中的一名女子请求亲自回应指控。使者坚持，教义问题只能由受圣秩的男子发言。村民回答，信仰不会让男女有不同的价值。这场听证将接纳她的证词，或遵循使者的程序。','Une femme de l’assemblée demande à répondre elle-même aux accusations. L’envoyé insiste : seul un homme ordonné peut parler de doctrine. Les villageois répliquent que la foi ne donne pas une valeur différente aux hommes et aux femmes. Mon audience admettra son témoignage ou suivra la procédure de l’envoyé.'),
 'c_apahunik',[
 (('She will speak before my court.','让她在我的宫廷发言。','Elle parlera devant ma cour.'),'add_learning_lifestyle_xp = 75 add_piety = -25 '+county_effect('c_apahunik','set_variable = { name = CAUC_tondrakian_equal_hearing value = 1 }')+' '+follow(142)),
 (('Follow the church’s procedure for this hearing.','此次听证依教会程序进行。','Suivre la procédure de l’Église pour cette audience.'),'add_piety = 25 '+county_effect('c_apahunik','set_variable = { name = CAUC_tondrakian_equal_hearing value = 0 }')+' '+follow(142))
 ],extra=CHRISTIAN)
event(142,('Fields Held in Common','共同持有的田地','Des champs détenus en commun'),
 ('The assembly’s account turns to land. Several families cultivate fields together and ask that the harvest support their households before any lord takes a rent. The church presents a deed claiming those fields. The dispute is no longer confined to worship: someone must decide who may collect the grain.','聚会的陈述转到了土地问题。几个家族共同耕种田地，请求收成先供养各户，再由领主收租。教会出示契据，声称这些田地归它所有。争论已不只关乎礼拜：必须有人裁定谁有权收粮。','Le récit de l’assemblée se tourne vers la terre. Plusieurs familles cultivent ensemble des champs et demandent que la récolte nourrisse leurs foyers avant qu’un seigneur n’en prélève le loyer. L’Église présente un acte de propriété. Le différend dépasse désormais le culte : il faut décider qui peut percevoir le grain.'),
 'c_apahunik',[
 (('Commission a survey before rents are collected.','征租前先行勘查。','Faire arpenter les terres avant de percevoir les loyers.'),'remove_short_term_gold = 25 '+county_effect('c_apahunik','change_county_control = 5')+' '+follow(143),'gold >= 25'),
 (('Suspend the disputed rents until my judgment.','裁决前暂停有争议的租赋。','Suspendre les loyers contestés jusqu’à mon jugement.'),'remove_short_term_gold = 10 add_prestige = -15 '+follow(143),'gold >= 10'),
 (('Keep the existing collections during the inquiry.','调查期间照旧征收。','Maintenir les perceptions pendant l’enquête.'),county_effect('c_apahunik','change_county_control = -4')+' '+follow(143))
 ],theme='stewardship',extra=CHRISTIAN)
adopt_rite = 'set_character_rite = rite:CAUC_tondrakian_rite '+county_effect('c_apahunik','set_county_rite = rite:CAUC_tondrakian_rite')
event(143,('The Ruler’s Judgment','统治者的裁决','Le jugement du dirigeant'),
 ('I have heard the accusations and the villagers’ replies. They ask for assemblies without images, common property and the right to resist those who oppress them. Their spokespeople insist that men and women must stand as equals. I can shelter the community, enforce the church’s prohibition, or adopt their rite myself.','指控与村民的答辩，我都已听过。他们要求不设圣像的聚会、共同财产，以及反抗压迫者的权利。代表们坚持，男女必须平等。我可以庇护这一社群、执行教会禁令，或亲自改奉他们的礼制。','J’ai entendu les accusations et les réponses des villageois. Ils demandent des assemblées sans images, des biens communs et le droit de résister à ceux qui les oppriment. Leurs porte-parole insistent sur l’égalité des hommes et des femmes. Je peux protéger la communauté, appliquer l’interdiction de l’Église ou adopter moi-même leur rite.'),
 'c_apahunik',[
 (('Protect their assemblies without adopting the rite.','保护聚会，但不改奉礼制。','Protéger leurs assemblées sans adopter le rite.'),clear_policy('c_apahunik',ton_mods)+policy('c_apahunik',ton_mods[0])+state('c_apahunik','tondrakian_inquiry',4)+' add_piety = -100 '+follow(144)),
 (('Close the assemblies and uphold the prohibition.','取缔聚会，维持禁令。','Fermer les assemblées et maintenir l’interdiction.'),clear_policy('c_apahunik',ton_mods)+policy('c_apahunik',ton_mods[1])+state('c_apahunik','tondrakian_inquiry',5)+' add_piety = 100 '+county_effect('c_apahunik','change_county_control = -8')+' '+follow(144)),
 (('I will stand with them as a Tondrakian.','我将作为通德拉基派与他们站在一起。','Je me tiendrai à leurs côtés comme tondrakien.'),'add_piety = -500 '+adopt_rite+' '+clear_policy('c_apahunik',ton_mods)+policy('c_apahunik',ton_mods[2])+state('c_apahunik','tondrakian_inquiry',6)+' '+follow(144),'faith = faith:armenian_apostolic piety >= 500')
 ],extra=CHRISTIAN)
event(144,('After the Judgment','裁决之后','Après le jugement'),
 ('My judgment has reached the villages. The decision over assemblies, rents and religious authority will shape their dealings with my officers. A clerk offers to record the terms and the testimony heard, so that the next dispute cannot erase what was promised.','裁决已经传到村庄。聚会、租赋与宗教权威的处置，将影响村民与我的官员打交道的方式。书记愿意记录条款与听证证词，免得下次争论抹去今日的承诺。','Mon jugement est parvenu aux villages. La décision sur les assemblées, les loyers et l’autorité religieuse déterminera leurs relations avec mes officiers. Un clerc propose de consigner les conditions et les témoignages afin qu’un prochain différend n’efface pas les promesses.'),
 'c_apahunik',[
 (('Record the equal standing of women and men.','记下男女平等的地位。','Consigner l’égalité des femmes et des hommes.'),'add_learning_lifestyle_xp = 100 '+end('tondrakian_inquiry'),'exists = rite:CAUC_tondrakian_rite rite = rite:CAUC_tondrakian_rite title:c_apahunik = { var:CAUC_tondrakian_inquiry_choice = 6 }'),
 (('Put the settlement and its testimony in writing.','写下处置与听证证词。','Consigner le règlement et les témoignages.'),'remove_short_term_gold = 15 add_learning_lifestyle_xp = 75 '+end('tondrakian_inquiry'),'gold >= 15'),
 (('My officers will uphold the judgment.','由我的官员执行裁决。','Mes officiers feront respecter le jugement.'),'add_prestige = 15 '+end('tondrakian_inquiry'))
 ],extra=CHRISTIAN)
modifier(ton_mods[0],('Sheltered Tondrakian Assemblies','获庇护的通德拉基聚会','Assemblées tondrakiennes protégées'),('The ruler shelters the community, while opponents dispute its assemblies and common property.','统治者庇护这一社群，但反对者仍质疑其聚会与共同财产。','Le dirigeant protège la communauté, mais ses opposants contestent ses assemblées et ses biens communs.'),'county_opinion_add = 5 tax_mult = -0.08')
modifier(ton_mods[1],('Tondrakian Assemblies Suppressed','通德拉基聚会受镇压','Assemblées tondrakiennes réprimées'),('Religious authorities welcome the prohibition, but enforcement unsettles the villages.','宗教权威欢迎禁令，但执行镇压使村庄不安。','Les autorités religieuses saluent l’interdiction, mais son application trouble les villages.'),'county_opinion_add = -12 tax_mult = 0.05')
modifier(ton_mods[2],('Tondrakian Common Assembly','通德拉基共同聚会','Assemblée commune tondrakienne'),('The ruler and county adopt the Tondrakian rite, supporting equal participation and common holdings.','统治者与本县改奉通德拉基礼制，支持平等参与和共同财产。','Le dirigeant et le comté adoptent le rite tondrakien, soutenant la participation égale et les biens communs.'),'county_opinion_add = 10 tax_mult = -0.08 levy_size = 0.05')
loc('CAUC_tondrakian_rite','Tondrakian Rite','通德拉基礼制','Rite tondrakien')
loc('CAUC_tondrakian_rite_adj','Tondrakian','通德拉基派','tondrakienne')
loc('CAUC_tondrakian_rite_adherent','Tondrakian','通德拉基派信徒','tondrakien')
loc('CAUC_tondrakian_rite_adherent_plural','Tondrakians','通德拉基派信徒','tondrakiens')
loc('CAUC_smbat_zarehavantsi_name','Smbat Zarehavantsi','斯姆巴特·扎雷哈万齐','Smbat Zarehavantsi')
loc('CAUC_tondrakian_rite_desc',
 'An Armenian Apostolic branch rite associated with the assemblies of Tondrak. $generic_rite_focus_tenet_aniconism$',
 '与通德拉克聚会社群相关的亚美尼亚使徒教会分支礼制。$generic_rite_focus_tenet_aniconism$',
 'Un rite apostolique arménien associé aux assemblées de Tondrak. $generic_rite_focus_tenet_aniconism$')
loc('CAUC_tondrakian_rite_founded_desc',
 "[ROOT.Rite.GetNameNoTooltip] was founded by [GetGlobalVariable('CAUC_tondrakian_founder').Char.GetFullName] in [GetGlobalVariable('CAUC_tondrakian_origin').Title.GetNameNoTier] in [GetGlobalVariable('CAUC_tondrakian_founding_year').GetValue|0], as a rite within the [ROOT.Rite.GetFaith.GetAdjective] faith. [ROOT.Rite.Custom('GetGenericRiteTenetSentence')]",
 "[ROOT.Rite.GetNameNoTooltip]由[GetGlobalVariable('CAUC_tondrakian_founder').Char.GetFullName]于[GetGlobalVariable('CAUC_tondrakian_founding_year').GetValue|0]年在[GetGlobalVariable('CAUC_tondrakian_origin').Title.GetNameNoTier]创立，是[ROOT.Rite.GetFaith.GetAdjective]信仰的分支礼制。[ROOT.Rite.Custom('GetGenericRiteTenetSentence')]",
 "[ROOT.Rite.GetNameNoTooltip] a été fondé par [GetGlobalVariable('CAUC_tondrakian_founder').Char.GetFullName] à [GetGlobalVariable('CAUC_tondrakian_origin').Title.GetNameNoTier] en [GetGlobalVariable('CAUC_tondrakian_founding_year').GetValue|0], au sein de la foi [ROOT.Rite.GetFaith.GetAdjective]. [ROOT.Rite.Custom('GetGenericRiteTenetSentence')]")

def main():
 from overhaul_stories import overhaul
 overhaul(EVENTS, DECISIONS, MODIFIERS, FLOWS, LOC)
 write(ROOT/'events/CAUC_religious_events.txt', '# Optional regional stories; delayed stages recheck direct ownership.\nnamespace = CAUC\n\n'+'\n'.join(EVENTS))
 write(ROOT/'common/decisions/CAUC_religious_decisions.txt', '\n'.join(DECISIONS))
 write(ROOT/'common/modifiers/CAUC_religious_modifiers.txt', '\n'.join(MODIFIERS))
 for lang in LANGS:
  values = LOC[lang]
  assert all('"' not in value and '\n' not in value for value in values.values())
  write(ROOT/'localization'/lang/('CAUC_religious_l_'+lang+'.yml'), 'l_'+lang+':\n'+'\n'.join(' '+key+':0 "'+value+'"' for key,value in values.items()))
 report = {'flows':FLOWS,'decisions':len(DECISIONS),'events':len(EVENTS),'county_modifiers':len(MODIFIERS),'translated_keys_per_language':len(LOC['english']),'complete_languages':list(LANGS),'new_rite':'CAUC_tondrakian_rite','parent_faith':'armenian_apostolic','uses_native_rite_effects':True,'icon':'gfx/interface/icons/faith/CAUC_tondrakian.dds','mass_realm_conversion':False,'founder_generation':'Native-style historical-character template; lifespan adapted to outbreak year','founder':'Smbat Zarehavantsi','founder_culture':'armenian','founder_dynasty':'none; Zarehavantsi is geographic, hereditary lineage unattested','founder_reference_persists_after_death':True}
 rite_fields = dict((key,value) for key,value,_,_ in entries(entries((ROOT/'common/religion/rite_types/CAUC_tondrakian_rite_types.txt').read_text(encoding='utf-8-sig'))[0][1]))
 report['tenets'] = canonical(rite_fields['tenets'])
 report['doctrines'] = canonical(rite_fields['doctrines'])
 (ROOT/'research/religious-content.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__':
 main()

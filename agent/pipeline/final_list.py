# Итоговый ручной отбор ОПЕРАТОРОВ (B2C) с присутствием на Кипре.
# (категория, название, бренды/юрлицо, сайт, [варианты LinkedIn-slug], источники, уверенность, заметка)
NBA = "1. Лицензия NBA Кипр (официальный реестр)"
ONL = "2. Онлайн-оператор с офисом/HQ на Кипре"
HIR = "3. Онлайн-оператор, нанимает на Кипре (HQ в другой стране)"
LAND = "4. Наземные казино / ставки (Кипр)"
QQ = "5. Под вопросом (гибрид оператор+B2B или слабое подтверждение)"
NC = "6. Северный Кипр"

ROWS = [
 # --- официальный реестр NBA (nba.gov.cy, Class A/B) ---
 (NBA,"bet365 Cyprus","Hillside (New Media Cyprus) Ltd; лиц. B001","https://www.bet365.com.cy",["bet365"],"NBA",'high',"Офис в Лимасоле; HQ группы — Великобритания"),
 (NBA,"Bet on Alfa","Bet On Alfa Ltd; A005+B005","https://www.betonalfa.com.cy",["betonalfa"],"NBA, LinkedIn",'high',""),
 (NBA,"Winmasters","Level Up Interactive Ltd; B004","https://www.winmasters.com.cy",["winmasters"],"NBA, Apollo",'high',""),
 (NBA,"UBET","U.B.E.T. Ultimate Bet Entertainment Technologies Ltd; B008","https://www.ubet.com.cy",["ubet-cyprus","ubetcy","ubet"],"NBA",'high',"Лицензия с 04.2026"),
 (NBA,"Meridianbet (Meridian Gaming CY)","Meridian Gaming (CY) Ltd; A013+B009","https://www.meridianbet.com.cy",["meridianbet-com"],"NBA, Apollo",'high',"Группа на Nasdaq; кипрский офис в Лимасоле"),
 (NBA,"Megabet Plus / Scorebet","Cleverpath Holdings Ltd; A014+B011","https://www.megabetplus.com.cy",["megabetplus"],"NBA, LinkedIn",'high',"Крупнейшая сеть точек на Кипре; Scorebet — второй бренд"),
 (NBA,"Fonbet Cyprus","Fortune Entertainment RG Ltd; B012","https://www.fonbet.com.cy",["fonbet"],"NBA, LinkedIn",'high',""),
 (NBA,"in2bet","I.T.S. Infinity Technology Solutions CY Ltd; B016","https://www.in2bet.com.cy",["in2bet"],"NBA, StepRole",'high',""),
 (NBA,"Allwynbet / Allwyn Cyprus","OPAP Sports Ltd; A007+B017","https://www.allwynbet.com.cy",["opap-sports-ltd","allwyn-cyprus"],"NBA, Apollo",'high',"Также лотереи Allwyn Cyprus"),
 (NBA,"Stoiximan (Kaizen Gaming)","Stoiximan Ltd; B018","https://www.stoiximan.com.cy",["kaizen-gaming","stoiximan"],"NBA, LinkedIn",'high',"HQ Kaizen — Афины"),
 (NBA,"CopyBet","Copybet EU Ltd; B020","https://www.copybet.com.cy",["copybet"],"NBA, LinkedIn",'high',"Кипрский офис в Лимасоле"),
 (NBA,"Cybet","Betathlon Ltd; A002+B021","https://www.cybet.com.cy",["betathlon-ltd-cybet"],"NBA, LinkedIn",'high',""),
 (NBA,"Novibet","Gamart Ltd; B022","https://www.novibet.com.cy",["novibet"],"NBA, LinkedIn",'high',"51% у Allwyn"),
 (NBA,"BookieCo","BookieCo Betting Stores Ltd; A016","https://bookieco.com.cy",["bookieco"],"NBA, LinkedIn",'high',"Наземные точки, Ларнака"),
 # --- онлайн-операторы с HQ/офисом на Кипре ---
 (ONL,"Parimatch","Parimatch","https://parimatch.com",["parimatch-cyprus"],"LinkedIn (HQ Limassol), вакансии",'high',"Активно нанимает на Кипре"),
 (ONL,"1xBet","1xBet","https://1xbet.com",["1xbet-official","1xbet"],"LinkedIn, Wikipedia",'high',"10 000+ сотрудников"),
 (ONL,"Melbet","Melbet","https://melbet.com",["melbetaffiliates","melbetco"],"LinkedIn (Nicosia), StepRole",'high',""),
 (ONL,"22Bet","22Bet","https://22bet.com",["22bet"],"LinkedIn (Nicosia), вакансии",'high',"Страница LinkedIn называется 22BET PARTNERS"),
 (ONL,"BetWinner","BetWinner","https://betwinner.com",["betwinner"],"LinkedIn (Nicosia)",'high',""),
 (ONL,"Megapari","Megapari","https://megapari.com",["megapari"],"LinkedIn, StepRole, Apollo",'high',""),
 (ONL,"Linebet","Linebet","https://linebet.com",["linebet"],"LinkedIn (HQ Limassol)",'high',"1 000–5 000 сотрудников"),
 (ONL,"HelaBet","HelaBet","https://helabet.com",["helabet"],"LinkedIn (HQ Limassol)",'high',""),
 (ONL,"PariPesa","Paripes Ltd","https://paripesa.com",["paripesa"],"LinkedIn (HQ Limassol)",'high',""),
 (ONL,"SpinBetter","SpinBetter","https://spinbetter.com",["spinbetter"],"LinkedIn, Apollo",'high',""),
 (ONL,"888STARZ","888STARZ","https://888starz.bet",["888starz","888starz-partners"],"LinkedIn, Apollo, StepRole",'medium',"Найдена партнёрская страница"),
 (ONL,"1xSlots","1xSlots","https://1xslot.com",["1xslots-online-casino","1xslots"],"StepRole (Nicosia), Apollo",'medium',""),
 (ONL,"Betcart","Betcart","https://www.betcart.com",["betcart"],"LinkedIn (HQ Limassol)",'high',""),
 (ONL,"RISK","RISK (risk.inc)","https://risk.inc",["riskinc"],"LinkedIn (HQ Limassol), вакансии, Apollo",'high',"1 000–5 000 сотрудников; много вакансий"),
 (ONL,"Stake","Stake.com","https://stake.com",["stake-com","stakecom"],"LinkedIn, StepRole (Nicosia), Apollo",'medium',"Кипрский офис по данным StepRole/Apollo"),
 (ONL,"Roobet","Roobet","https://roobet.com",["roobet"],"StepRole (Limassol)",'medium',""),
 (ONL,"EGO – EGamingOnline","EUcasino, RedKings, SlotsMagic, Drueckglueck и др.","https://www.egamingonline.com",["egamingonline"],"LinkedIn (HQ Limassol)",'medium',"Страница — аффилиат-программа брендов"),
 (ONL,"TLF Entertainment","4 бренда онлайн-казино","https://www.tlf.com",["tlf-mng"],"LinkedIn, StepRole, Apollo",'medium',""),
 (ONL,"CasinoSecret","CasinoSecret","https://www.casinosecret.com",["casinosecret"],"LinkedIn (HQ Limassol)",'medium',"Онлайн-казино с кэшбэком"),
 (ONL,"Wikibet","Wikibet","https://www.wikibet.com",["wikibet"],"LinkedIn (HQ Limassol)",'medium',""),
 (ONL,"ATMBET","ATMBET","https://www.atmbet.com",["atmbet"],"LinkedIn (HQ Limassol)",'medium',""),
 (ONL,"AlienBet","alienbet.com","https://alienbet.com",["alienbet"],"LinkedIn, StepRole (Larnaca)",'medium',""),
 (ONL,"Rolletto","Rolletto.com","https://rolletto.com",["rolletto","rollettocom"],"StepRole (Nicosia), Apollo",'medium',""),
 (ONL,"LOOT.BET","Livestream Ltd (React Gaming Group)","https://loot.bet",["lootbet","loot-bet"],"StepRole (Nicosia), Apollo",'medium',"Эспорт-беттинг"),
 (ONL,"Vulkan Vegas","Vulkan Vegas","https://vulkanvegas.com",["vulkan-vegas","vulkanvegas"],"StepRole (Limassol)",'low',""),
 (ONL,"Mega Dice Casino","Mega Dice","https://www.megadice.com",["megadice","mega-dice-casino"],"StepRole",'low',"Крипто-казино"),
 (ONL,"Cazimbo Casino","Cazimbo","https://www.cazimbo.com",["cazimbo","cazimbo-casino"],"StepRole (Nicosia)",'low',""),
 (ONL,"Betvili","Betvili","",["betvili"],"StepRole (Nicosia)",'low',""),
 (ONL,"CrazyBet","CrazyBet","https://crazybet.com",["crazybet"],"Apollo (HQ Cyprus)",'medium',""),
 (ONL,"WinnersHall Online Casino","WinnersHall","https://winnershall.com",["winnershall","winnershall-online-casino"],"Apollo (HQ Cyprus)",'medium',""),
 (ONL,"BetMidas","BetMidas","https://betmidas.net",["betmidas"],"Apollo (HQ Cyprus)",'low',""),
 (ONL,"Mad Money Casino","Mad Money Casino","https://madmoneycasino.com",["mad-money-casino","madmoneycasino"],"Apollo (HQ Cyprus)",'low',""),
 (ONL,"WPT Global","WPT Global (покер)","https://wptglobal.com",["wpt-global","wptglobal"],"Apollo (HQ Cyprus)",'medium',"Онлайн-покер"),
 (ONL,"PokerMatch","PokerMatch (покер)","https://pokermatch.com",["pokermatch"],"Apollo (HQ Cyprus)",'medium',"Онлайн-покер"),
 (ONL,"CSGORoll","CSGORoll","https://csgoroll.com",["csgoroll"],"Apollo (HQ Cyprus)",'medium',"Скины/кейсы, gambling-продукт"),
 (ONL,"DBbet","DBbet","https://db-bet.com",["dbbet","db-bet"],"Apollo (HQ Cyprus)",'low',""),
 (ONL,"Twinsbet","Twinsbet Global","https://twin.com",["twinsbet","twinsbet-global"],"Apollo (HQ Cyprus)",'low',""),
 (ONL,"Bullsbet","Bullish Entertainment B.V.","https://bullsbet.io",["bullsbet","bullish-entertainment"],"Apollo (HQ Cyprus)",'low',""),
 (ONL,"4RABET","4RABET","https://4rabet-web.com",["4rabet"],"Apollo (HQ Cyprus)",'medium',"Рынок Индии"),
 (ONL,"Paridirect","Paridirect","http://www.paridirect.com",["paridirect"],"StepRole",'low',"Африка"),
 (ONL,"tether.bet","tether.bet","https://www.tether.bet",["tetherbet","tether-bet"],"StepRole",'low',"Крипто"),
 (ONL,"Grailbet","Grail Technologies Ltd (Сент-Люсия)","https://www.grailbet.com",["grailbet"],"Вакансии в Лимасоле",'low',""),
 (ONL,"Betfinal","Final Enterprises N.V.","https://www.betfinal.com",["betfinal"],"Платёжный агент в Никосии",'low',""),
 (ONL,"Mostbet","Venson Ltd","https://mostbet.com",["mostbet"],"Apollo: Mostbet Partners с HQ на Кипре",'low',""),
 # --- нанимают на Кипре, HQ в другой стране ---
 (HIR,"VBET","VBET","https://www.vbet.com",["vbet-official"],"Вакансии LinkedIn на Кипре (C-level, маркетинг)",'medium',"HQ — Мальта"),
 (HIR,"SkillOnNet (PlayOJO)","SkillOnNet","https://www.skillonnet.com",["skillonnet"],"Вакансии LinkedIn на Кипре",'medium',"HQ — Мальта; бренды PlayOJO и др."),
 (HIR,"Betsson Group","Betsson","https://www.betssongroup.com",["betsson-group"],"LinkedIn: офис на Кипре",'medium',"HQ — Мальта"),
 (HIR,"CoinPoker","CoinPoker","https://coinpoker.com",["thecoinpoker"],"Вакансии LinkedIn на Кипре",'medium',"Крипто-покер"),
 (HIR,"Blitzed","Blitzed Casino","",["blitzed-casino"],"Вакансии LinkedIn на Кипре",'low',""),
 # --- наземные ---
 (LAND,"City of Dreams Mediterranean / Cyprus Casinos","Integrated Casino Resorts Cyprus Ltd (Melco)","https://www.cityofdreamsmed.com.cy",["city-of-dreams-mediterranean","cyprus-casinos"],"LinkedIn, Apollo",'high',"Единственный легальный оператор казино в РК"),
 (LAND,"Maxbet Entertainment Group","Maxbet Entertainment Group Plc","https://www.maxbetgroup.com",["maxbet-entertainment-group-plc"],"LinkedIn (HQ Limassol)",'high',"Слот-залы в ЦВЕ"),
 # --- под вопросом ---
 (QQ,"1win","1WIN N.V.","https://1win.com",["1win-global","1win-group"],"LinkedIn, Apollo",'medium',"Позиционируется как B2B-экосистема, но главный бренд — B2C"),
 (QQ,"Soft2Bet","Estata Ltd","https://soft2bet.com",["soft2bet"],"вакансии, LinkedIn",'medium',"Оператор 60+ брендов и B2B-платформа"),
 (QQ,"PIN-UP Global (RedCore)","Carletta Ltd (Никосия)","https://pin-up.global",["pin-up-global"],"LinkedIn, StepRole",'medium',"Сейчас B2B-холдинг"),
 (QQ,"MINT","mint.io","https://mint.io",["mintcasino"],"LinkedIn, Apollo",'low',"Web3 iGaming-платформа"),
 # --- Северный Кипр ---
 (NC,"Hititbet","Hititbet","https://www.hititbet.com",["hititbet"],"LinkedIn",'medium',""),
 (NC,"Merit International Casinos","Net Holding","",["meritcasinos"],"LinkedIn",'high',"5 отелей-казино"),
 (NC,"Elexus Hotel & Casino","Elexus","",["elexus-hotel-&-resort-&-casino"],"LinkedIn",'high',""),
 (NC,"Concorde Casinos","Concorde","https://concordecasinos.com",["concorde-casinos","concordecasinos"],"Apollo",'medium',""),
 (NC,"Kaya Artemis","Kaya Artemis","https://kayaartemis.com.tr",["kaya-artemis","kayaartemis"],"Apollo",'medium',""),
]

# --- добавлено по результатам поиска Lusha (Cyprus + Gambling Facilities & Casinos, 132 компании) ---
ROWS += [
 (LAND,"Ritzio Entertainment Group","Ritzio (игровые залы)","https://www.ritzio.eu",[],"Lusha (HQ Nicosia)",'medium',"Оператор игровых залов в Европе/СНГ"),
 (NC,"Pasha International","Pasha (казино)","https://www.pashainternational.com",[],"Lusha",'medium',"Казино-оператор"),
 (ONL,"ClubWPT Gold","ClubWPT Gold (покер)","https://www.clubwptgold.com",[],"Lusha",'medium',"Покер, sweepstakes"),
 (ONL,"Gaming Point","Gaming Point — Online Casino & Sports Betting","https://www.gamingpoint.co",[],"Lusha, Apollo, StepRole (Limassol)",'medium',"Есть партнёрка GamingPoint Affiliates"),
 (ONL,"EuroCasinoBet","EuroCasinoBet Ltd","https://www.eurocasinobet.com",[],"Lusha",'low',""),
 (ONL,"Wowbet","Wowbet","https://www.wowbet.win",[],"Lusha (страница партнёрки)",'low',""),
 (ONL,"Opabet","Opabet","https://www.opabet.com",[],"Lusha (страница партнёрки, Nicosia)",'low',""),
 (ONL,"Millionaires Gaming Africa","Millionaires Gaming","https://www.millionairesgamingafrica.com",[],"Lusha",'low',"Рынок Африки"),
 (ONL,"All The Best Lottos","Онлайн-лотереи","https://www.allthebestlottos.com",[],"Lusha (Nicosia)",'low',"Лотереи"),
 (ONL,"Lotto Agent","Онлайн-лотереи","https://www.agentlotto.com",[],"Lusha",'low',"Лотереи"),
]
# LinkedIn из базы Lusha (приоритет, если прямая проверка не удалась)
LUSHA_LI = {
 "in2bet":"https://www.linkedin.com/company/in2bet-cy",
 "Rolletto":"https://www.linkedin.com/company/rolletto-com",
 "DBbet":"https://www.linkedin.com/company/dbbet-team",
 "Megabet Plus / Scorebet":"https://www.linkedin.com/company/megabetplus",
 "Ritzio Entertainment Group":"https://www.linkedin.com/company/ritzio-entertainment-group",
 "Pasha International":"https://www.linkedin.com/company/pasha-international",
 "ClubWPT Gold":"https://www.linkedin.com/company/clubwptgold",
 "Gaming Point":"https://www.linkedin.com/company/gaming-point",
 "EuroCasinoBet":"https://www.linkedin.com/company/eurocasinobet-ltd",
 "Wowbet":"https://www.linkedin.com/company/wowbet-parthers",
 "Opabet":"https://www.linkedin.com/company/opabet",
 "Millionaires Gaming Africa":"https://www.linkedin.com/company/millionaires-gaming-africa-ghana",
 "All The Best Lottos":"https://www.linkedin.com/company/allthebestlottos",
 "Lotto Agent":"https://www.linkedin.com/company/lotto-agent",
}
LUSHA_SIZE = {"Ritzio Entertainment Group":"1,001-5,000","Pasha International":"5,001-10,000","ClubWPT Gold":"51-200",
 "Gaming Point":"11-50","EuroCasinoBet":"11-50","Wowbet":"51-200","Opabet":"11-50","Millionaires Gaming Africa":"1,001-5,000",
 "All The Best Lottos":"201-500","Lotto Agent":"11-50","in2bet":"11-50","Rolletto":"51-200","DBbet":"51-200","BetWinner":"201-500"}
LUSHA_HQ = {"Ritzio Entertainment Group":"Nicosia","ClubWPT Gold":"Cyprus","Gaming Point":"Limassol","Opabet":"Nicosia",
 "All The Best Lottos":"Nicosia","in2bet":"Cyprus","Rolletto":"Nicosia","DBbet":"Nicosia","BetWinner":"Nicosia",
 "Pasha International":"Cyprus","EuroCasinoBet":"Cyprus","Wowbet":"Cyprus","Millionaires Gaming Africa":"Cyprus","Lotto Agent":"Cyprus"}

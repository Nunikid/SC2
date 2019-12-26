import sc2
from sc2 import Race, Difficulty
from sc2 import maps, run_game
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.player import Bot, Computer
from sc2.player import Human
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.units import Units
from sc2.ids.upgrade_id import UpgradeId


class Vinc3nt(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_supply()
		await self.lower_depot()
		await self.expansion()
		await self.build_barracks()
		await self.build_refinery()
		await self.ccmorph()
		await self.mules()
		await self.marines()
		await self.attackmarines()
		await self.morebarracks()
		await self.more_workers1()
		await self.build_engineeringbay()
		await self.upgradearmor1()
		await self.upgradeweapon1()
		await self.more_workers2()
		await self.more_supply()
		await self.build_factory()
		await self.build_armory()
		await self.upgradetier2()
		await self.boombarracks()

		
	async def build_workers(self):
		for th in self.townhalls.idle:
			if (
				self.can_afford(UnitTypeId.SCV) 
				and self.supply_left > 0
				and self.supply_workers < 19
				and (
					self.structures(UnitTypeId.BARRACKS).ready.amount < 1 
					and self.townhalls(UnitTypeId.COMMANDCENTER).idle 
					or self.townhalls(UnitTypeId.ORBITALCOMMAND).idle
				)
			):
					self.do(th.train(UnitTypeId.SCV), subtract_cost=True, subtract_supply=True)
	async def build_supply(self):
		if self.supply_left < 7 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
			workers = self.workers.gathering
			worker = workers.furthest_to(workers.center)
			location = await self.find_placement(UnitTypeId.SUPPLYDEPOT, worker.position, placement_step=3)
			if location:
				if self.can_afford(UnitTypeId.SUPPLYDEPOT):
					self.do(worker.build(UnitTypeId.SUPPLYDEPOT, location), subtract_cost=True)

	async def lower_depot(self):
		for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
			self.do(depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER))
	async def ccmorph(self):
		orbital_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.ORBITALCOMMAND)
		if orbital_tech_requirement == 1:
			for cc in self.townhalls(UnitTypeId.COMMANDCENTER).idle:
				if self.can_afford(UnitTypeId.ORBITALCOMMAND):
					self.do(cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND),subtract_cost=True)
	async def build_barracks(self):
		barracks_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.BARRACKS)
		if (
			barracks_tech_requirement == 1
			and self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) < 2
			and self.can_afford(UnitTypeId.BARRACKS)
		):
			workers = self.workers.gathering
			if (
				workers and self.townhalls
			):
				worker = workers.furthest_to(workers.center)
				location = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=5)
				if location:
					self.do(worker.build(UnitTypeId.BARRACKS, location), subtract_cost=True)
	async def build_refinery(self):
		for th in self.townhalls.ready:
			vgs = self.vespene_geyser.closer_than(10, th)
			for vg in vgs:
				if await self.can_place(UnitTypeId.REFINERY, vg.position) and self.can_afford(UnitTypeId.REFINERY) and self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) >= 3 and (self.already_pending(UnitTypeId.REFINERY) + self.structures(UnitTypeId.REFINERY).ready.amount < 1):
					workers = self.workers.gathering
					if workers:
						worker = workers.closest_to(vg)
						self.do(worker.build(UnitTypeId.REFINERY, vg), subtract_cost=True)
						break
	async def expansion(self):
		if (
			1 <= self.townhalls.amount < 6
			and self.already_pending(UnitTypeId.COMMANDCENTER) == 0
			and self.can_afford(UnitTypeId.COMMANDCENTER)
		):
			location = await self.get_next_expansion()
			if location:
				worker = self.select_build_worker(location)
				if worker and self.can_afford(UnitTypeId.COMMANDCENTER):
					self.do(worker.build(UnitTypeId.COMMANDCENTER, location), subtract_cost=True)

	async def mules(self):
		for oc in self.townhalls(UnitTypeId.ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
			mfs = self.mineral_field.closer_than(10, oc)
			if mfs:
				mf = max(mfs, key=lambda x: x.mineral_contents)
				self.do(oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mf))
	async def marines(self):
		if self.supply_left > 0 and self.supply_army < 60:
			for rax in self.structures(UnitTypeId.BARRACKS).idle:
				if self.can_afford(UnitTypeId.MARINE):
					self.do(rax.train(UnitTypeId.MARINE), subtract_cost=True, subtract_supply=True)
	async def attackmarines(self):
		marines: Units = self.units(UnitTypeId.MARINE).idle
		if marines.amount >= 20:
			target = self.enemy_structures.random_or(self.enemy_start_locations[0]).position
			for marine in marines:
				self.do(marine.attack(target))
	async def morebarracks(self):
		barracks_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.BARRACKS)
		if(
			barracks_tech_requirement == 1
			and self.townhalls.amount >= 2
			and self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) < 10
			and self.can_afford(UnitTypeId.BARRACKS)
			):
				workers = self.workers.gathering
				if(
				workers and self.townhalls
			):
					worker = workers.furthest_to(workers.center)
				location = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=5)
				if location:
					self.do(worker.build(UnitTypeId.BARRACKS, location), subtract_cost=True)
	async def more_workers1(self):
		for th in self.townhalls.idle:
			if(
				self.can_afford(UnitTypeId.SCV) 
				and self.supply_left > 0
				and self.supply_workers < 37
				and self.townhalls.amount >= 2
				and self.can_afford(UnitTypeId.SCV)
				and (
				self.structures(UnitTypeId.BARRACKS).ready.amount < 1 
				and self.townhalls(UnitTypeId.COMMANDCENTER).idle 
				or self.townhalls(UnitTypeId.ORBITALCOMMAND).idle
				)
		):
				self.do(th.train(UnitTypeId.SCV), subtract_cost=True, subtract_supply=True)
	async def build_engineeringbay(self):
		marines: Units = self.units(UnitTypeId.MARINE).idle
		if marines.amount > 8 and (self.structures(UnitTypeId.ENGINEERINGBAY).ready.amount + self.already_pending(UnitTypeId.ENGINEERINGBAY) < 1):
			workers = self.workers.gathering
			worker = workers.furthest_to(workers.center)
			location = await self.find_placement(UnitTypeId.ENGINEERINGBAY, self.townhalls.random.position, placement_step=5)
			if location:
				if self.can_afford(UnitTypeId.ENGINEERINGBAY):
					self.do(worker.build(UnitTypeId.ENGINEERINGBAY, location), subtract_cost=True)

	async def upgradearmor1(self):
		if self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
				engineeringbay_ready = self.structures(UnitTypeId.ENGINEERINGBAY).ready
				if engineeringbay_ready:
					self.research(UpgradeId.TERRANINFANTRYARMORSLEVEL1)
	async def upgradeweapon1(self):
		if self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) == 0 and self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
				engineeringbay_ready = self.structures(UnitTypeId.ENGINEERINGBAY).ready
				if engineeringbay_ready:
					self.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
	async def more_workers2(self):
		for th in self.townhalls.idle:
			if(
				self.can_afford(UnitTypeId.SCV) 
				and self.supply_left > 0
				and self.supply_workers < 44
				and self.townhalls.amount >= 3
				and self.can_afford(UnitTypeId.SCV)
				and (
				self.structures(UnitTypeId.BARRACKS).ready.amount < 1 
				and self.townhalls(UnitTypeId.COMMANDCENTER).idle 
				or self.townhalls(UnitTypeId.ORBITALCOMMAND).idle
				)
		):
				self.do(th.train(UnitTypeId.SCV), subtract_cost=True, subtract_supply=True)
	async def more_supply(self):
		if self.townhalls.amount >= 3 and self.already_pending(UnitTypeId.SUPPLYDEPOT) <= 2:
			workers = self.workers.gathering
			worker = workers.furthest_to(workers.center)
			location = await self.find_placement(UnitTypeId.SUPPLYDEPOT, worker.position, placement_step=3)
			if location:
				if self.can_afford(UnitTypeId.SUPPLYDEPOT):
					self.do(worker.build(UnitTypeId.SUPPLYDEPOT, location), subtract_cost=True)
	async def build_factory(self):
		factory_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.FACTORY)
		if(
			factory_tech_requirement == 1
			and self.structures(UnitTypeId.ENGINEERINGBAY).ready.amount >= 1
			and self.structures(UnitTypeId.FACTORY).ready.amount + self.already_pending(UnitTypeId.FACTORY) < 1
			and self.can_afford(UnitTypeId.FACTORY)
			):
				workers = self.workers.gathering
				if(
				workers and self.townhalls
			):
					worker = workers.furthest_to(workers.center)
				location = await self.find_placement(UnitTypeId.FACTORY, self.townhalls.random.position, placement_step=5)
				if location:
					self.do(worker.build(UnitTypeId.FACTORY, location), subtract_cost=True)
	async def build_armory(self):
		armory_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.ARMORY)
		marines: Units = self.units(UnitTypeId.MARINE).idle
		if(
			armory_tech_requirement == 1
			and self.structures(UnitTypeId.ENGINEERINGBAY).ready.amount >= 1
			and self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1) == 0
			and self.structures(UnitTypeId.ARMORY).ready.amount + self.already_pending(UnitTypeId.ARMORY) <= 1
			and self.can_afford(UnitTypeId.ARMORY)
			):
				workers = self.workers.gathering
				if(
				workers and self.townhalls
			):
					worker = workers.furthest_to(workers.center)
				location = await self.find_placement(UnitTypeId.ARMORY, self.townhalls.random.position, placement_step=3)
				if location:
					self.do(worker.build(UnitTypeId.ARMORY, location), subtract_cost=True)
	async def upgradetier2(self):
		if self.structures(UnitTypeId.ARMORY).ready.amount >= 1:
			if self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL2):
				if self.structures(UnitTypeId.ENGINEERINGBAY).idle:
					self.research(UpgradeId.TERRANINFANTRYARMORSLEVEL2)
					self.research(UpgradeId.TERRANINFANTRYwEAPONSLEVEL2)
	async def boombarracks(self):
		barracks_tech_requirement: float = self.tech_requirement_progress(UnitTypeId.BARRACKS)
		if(
			barracks_tech_requirement == 1
			and self.townhalls.amount >= 5
			and self.structures(UnitTypeId.BARRACKS).ready.amount + self.already_pending(UnitTypeId.BARRACKS) < 15
			and self.can_afford(UnitTypeId.BARRACKS)
			):
				workers = self.workers.gathering
				if(
				workers and self.townhalls
			):
					worker = workers.furthest_to(workers.center)
				location = await self.find_placement(UnitTypeId.BARRACKS, self.townhalls.random.position, placement_step=5)
				if location:
					self.do(worker.build(UnitTypeId.BARRACKS, location), subtract_cost=True)




sc2.run_game(
    sc2.maps.get("AcropolisLE"),
    [Bot(Race.Terran, Vinc3nt()),
	Computer(Race.Zerg, Difficulty.Hard)
	], realtime=False)

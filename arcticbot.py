import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER
import random


class arcticbot(sc2.BotAI):
	async def on_step(self, iteration):
		await self.distribute_workers()
		await self.build_workers()
		await self.build_pylons()
		await self.build_more_pylons()
		await self.build_assimilators()
		await self.expand()
		await self.build_offensive_strukture()
		await self.build_offensive_units()
		await self.attack()

	def over_hundred_supply(self):
		if self.state.common.supply > 100:
			x = True
		else:
			x = False

		return bool(x)

	def find_targets(self, state):
		if len(self.known_enemy_units) > 0:
			return random.choice(self.known_enemy_units)
		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures)
		else:
			return self.enemy_start_locations[0]

	def gateway_countcount(self):
		x = self.units(NEXUS).amount * 4
		return int(x)

	def rechne_probecount(self):
		x = self.units(NEXUS).amount * 22 + 2
		return int(x)

	async def build_workers(self):
		for nexus in self.units(NEXUS).ready.noqueue:
			if self.can_afford(PROBE) and (self.units(PROBE).amount < self.rechne_probecount()):
				await self.do(nexus.train(PROBE))

	async def build_more_pylons(self):
		if  self.supply_left < 5 and not self.already_pending(PYLON) < 2:
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON) and self.over_hundred_supply:
					await self.build(PYLON, near=nexuses.random)
					await self.build(PYLON, near=nexuses.random)


	async def build_pylons(self):
		if self.supply_left < 5 and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=nexuses.first)
				

	async def build_assimilators(self):
		for nexus in self.units(NEXUS).ready:
			vaspenes = self.state.vespene_geyser.closer_than(10.0, nexus)
			for vaspene in vaspenes:
				if not self.can_afford(ASSIMILATOR):
					break
				worker = self.select_build_worker(vaspene.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists and self.state.common.vespene < 100:
					await self.do(worker.build(ASSIMILATOR, vaspene))

	async def expand(self):
		if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS) and self.units(GATEWAY).amount >=1:
			await self.expand_now()

	async def build_offensive_strukture(self):
		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random
			if self.units(GATEWAY).ready.exists:
				if not self.units(CYBERNETICSCORE):
					if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
						await self.build(CYBERNETICSCORE, near = pylon)
				else:
					if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and (self.units(GATEWAY).amount < self.gateway_countcount()):
								await self.build(GATEWAY, near = pylon)	
			else:
				if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
					await self.build(GATEWAY, near = pylon)

	async def build_offensive_units(self):
		for gw in self.units(GATEWAY).ready.noqueue:
			if self.can_afford(STALKER) and self.supply_left > 0 and self.units(NEXUS).amount >1:
				await self.do(gw.train(STALKER))

	async def attack(self):
		if self.units(STALKER).amount > 20:
			for s in self.units(STALKER).idle:
				await self.do(s.attack(self.find_targets(self.state)))

		if self.units(STALKER).amount > 5:
			if len(self.known_enemy_units) > 0:
				for s in self.units(STALKER).idle:
					await self.do(s.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("AbyssalReefLE"),[
	Bot(Race.Protoss, arcticbot()),
	Computer(Race.Terran, Difficulty.Hard)
	], realtime =False)


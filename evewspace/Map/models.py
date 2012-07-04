from django.db import models
from django.contrib.auth.models import Group
from evewspace.core.models import SystemData

# Create your models here.

class WormholeType(models.Model):
	"""Stores the permanent information on wormhole types. Any changes to this table should be made with caution."""
	name = models.CharField(max_length = 4, unique = True)
	maxmass = models.BigIntegerField()
	jumpmass = models.BigIntegerField()
	lifetime = models.IntegerField()
	target = models.CharField(max_length = 15)
	
	def __unicode__(self):
		"""Returns Wormhole ID as unicode representation."""
		return self.name


class System(SystemData):
	"""Stores the permanent record of a solar system. This table should not have rows added or removed through Django."""
	sysclass_choices = ((1, "C1"), (2, "C2"), (3, "C3"), (4, "C4"), (5, "C5"), (6, "C6"), (7, "High Sec"), (8, "Low Sec"), (9, "Null Sec"))
	sysclass = models.IntegerField(choices = sysclass_choices)
	occupied = models.TextField(blank = True)
	info = models.TextField(blank = True)
	lastscanned = models.DateTimeField()

	def __unicode__(self):
		"""Returns name of System as unicode representation"""
		return self.name

class KSystem(System):
	sov = models.CharField(max_length = 100)

class WSystem(System):
	static1 = models.ForeignKey(WormholeType, blank=True, null=True, related_name="primary_statics")
	static2 = models.ForeignKey(WormholeType, blank=True, null=True, related_name="secondary_statics")

class Map(models.Model):
	"""Stores the maps available in the map tool. root relates to System model."""
	name = models.CharField(max_length = 100, unique = True)
	root = models.ForeignKey(System, related_name="rootmaps")
	# Maps with explicitperms = True require an explicit permission entry to access.
	explicitperms = models.BooleanField()

	class Meta:
		permissions = (("map_restricted", "Require excplicit access to maps."),)

	def __unicode__(self):
		"""Returns name of Map as unicode representation."""
		return self.name


class MapSystem(models.Model):
	"""Stores information regarding which systems are active in which maps at the present time."""
	map = models.ForeignKey(Map, related_name="systems")
	system = models.ForeignKey(System, related_name="maps")
	friendlyname = models.CharField(max_length = 10)
	interesttime = models.DateTimeField()
	parentsystem = models.ForeignKey('self', related_name="childsystems")

	def __unicode__(self):
		return "system %s in map %s" % (self.system.name, self.map.name)

class Wormhole(models.Model):
	"""An instance of a wormhole in a  map. Wormhole have a 'top' and a
	'bottom', the top refers to the side that is found first (and
	the bottom is obviously the other side)"""
	map = models.ForeignKey(Map, related_name='wormholes')
	top = models.ForeignKey(MapSystem, related_name='child_wormholes')
	top_type = models.ForeignKey(WormholeType, related_name='+')
	bottom = models.ForeignKey(MapSystem, null=True, related_name='parent_wormholes') 
	bottom_type = models.ForeignKey(WormholeType, related_name='+')
	time_status = models.IntegerField(choices = ((0, "Fine"), (1, "End of Life")))
	mass_status = models.IntegerField(choices = ((0, "No Shrink"), (1, "First Shrink"), (2, "Critical")))


class SignatureType(models.Model):
	"""Stores the list of possible signature types for the map tool. Custom signature types may be added at will."""
	shortname = models.CharField(max_length = 6)
	longname = models.CharField(max_length = 100)

	def __unicode__(self):
		"""Returns short name as unicode representation"""
		return self.shortname

class Signature(models.Model):
	"""Stores the signatures active in all systems. Relates to System model."""
	system = models.ForeignKey(System, related_name="signatures")
	sigtype = models.ForeignKey(SignatureType, related_name="sigs")
	sigid = models.CharField(max_length = 10)

	def __unicode__(self):
		"""Returns sig ID as unicode representation"""
		return self.sigid
	
class Stargate(models.Model):
	"""Stargate jumps between systems from the Eve SDD. Every entry is repeated for both directions."""
	from_system = models.ForeignKey(System, related_name="fromjumps")
	to_system = models.ForeignKey(System, related_name="tojumps")

	def __unicode__(self):
		return "From: %s - To: %s" % (self.from_system.name, self.to_system.name)

class MapPermission(models.Model):
	"""Relates a user group to it's map permissions. Non-restricted groups will have change access to all maps."""
	group = models.ForeignKey(Group, related_name="mappermissions")
	map = models.ForeignKey(Map, related_name="grouppermissions")
	view = models.BooleanField()
	change = models.BooleanField()


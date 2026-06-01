from __future__ import annotations

from terminal.context import Context
from .base import BaseRotation


HAND_OF_GULDAN = "古尔丹之手"
FELHUNTER = "召唤地狱猎犬"
IMP = "召唤小鬼"
DREADSTALKERS = "召唤恐惧猎犬"
FELGUARD = "召唤恶魔卫士"
DEMONBOLT = "恶魔之箭"
SHADOW_BOLT = "暗影箭"
IMPLOSION = "内爆"
DOOMGUARD = "召唤末日守卫"
DEMONIC_TYRANT = "召唤恶魔暴君"


class WarlockDemonology(BaseRotation):
    name = "恶魔术灵魂收割者"
    desc = "恶魔学识术士灵魂收割者大秘境循环。"

    def __init__(self) -> None:
        super().__init__()

        self.macroTable = {
            f"target{HAND_OF_GULDAN}": "ALT-NUMPAD1",
            FELHUNTER: "ALT-NUMPAD2",
            IMP: "ALT-NUMPAD3",
            f"target{DREADSTALKERS}": "ALT-NUMPAD4",
            FELGUARD: "ALT-NUMPAD5",
            f"target{DEMONBOLT}": "ALT-NUMPAD6",
            f"target{SHADOW_BOLT}": "ALT-NUMPAD7",
            IMPLOSION: "ALT-NUMPAD8",
            f"target{DOOMGUARD}": "ALT-NUMPAD9",
            f"target{DEMONIC_TYRANT}": "ALT-NUMPAD0",
        }

    def main_rotation(self, ctx: Context) -> tuple[str, float, str]:
        if not ctx.enable:
            return self.idle("总开关未开启")

        if ctx.delay:
            return self.idle("延迟开关开启")

        spell_queue_window = float(ctx.spell_queue_window or 0.3)
        player = ctx.player
        target = ctx.target
        latest_succeeded_cast = ctx.latest_succeeded_cast

        if not player.alive:
            return self.idle("玩家已死亡")

        if player.isChatInputActive:
            return self.idle("正在聊天输入")

        if player.isMounted:
            return self.idle("骑乘中")

        if player.castIcon is not None:
            return self.idle("正在施法")

        if player.channelIcon is not None:
            return self.idle("正在引导")

        if player.isEmpowering:
            return self.idle("正在蓄力")

        if player.hasBuff("食物和饮料"):
            return self.idle("正在吃喝")

        if not player.isInCombat:
            return self.idle("未进入战斗")

        if not (target.exists and target.canAttack and target.isInRangedRange):
            return self.idle("没有合适的远程目标")

        soul_shards_cell = ctx.spec.cell(0)
        soul_shards_ratio = 0.0 if soul_shards_cell is None else soul_shards_cell.decimal
        soul_shards = round(soul_shards_ratio * 5)

        demon_core_stacks = player.buffStack("恶魔之核")
        dreadstalkers_ready = ctx.spell_cooldown_ready(
            DREADSTALKERS, spell_queue_window
        )
        implosion_ready = ctx.spell_cooldown_ready(IMPLOSION, spell_queue_window)
        hand_ready = ctx.spell_cooldown_ready(HAND_OF_GULDAN, spell_queue_window)
        demonbolt_ready = ctx.spell_cooldown_ready(DEMONBOLT, spell_queue_window)
        shadow_bolt_ready = ctx.spell_cooldown_ready(SHADOW_BOLT, spell_queue_window)
        tyrant_ready = ctx.spell_cooldown_ready(DEMONIC_TYRANT, spell_queue_window)
        doomguard_ready = ctx.spell_cooldown_ready(DOOMGUARD, spell_queue_window)

        is_aoe = player.enemyCount >= 3
        portal_window = player.hasBuff("阿古斯传送门")
        tyrant_window = player.hasBuff("恶魔暴君")

        if doomguard_ready and (tyrant_ready or tyrant_window or portal_window):
            return self.cast(f"target{DOOMGUARD}")

        if tyrant_ready and soul_shards >= 5:
            return self.cast(f"target{DEMONIC_TYRANT}")

        if portal_window or tyrant_window:
            if hand_ready and soul_shards >= 3:
                return self.cast(f"target{HAND_OF_GULDAN}")
            if demon_core_stacks >= 1 and demonbolt_ready:
                return self.cast(f"target{DEMONBOLT}")
            if dreadstalkers_ready and soul_shards >= 2:
                return self.cast(f"target{DREADSTALKERS}")

        if dreadstalkers_ready and soul_shards >= 2:
            return self.cast(f"target{DREADSTALKERS}")

        if is_aoe and implosion_ready and latest_succeeded_cast == HAND_OF_GULDAN:
            return self.cast(IMPLOSION)

        if hand_ready and soul_shards >= 4:
            return self.cast(f"target{HAND_OF_GULDAN}")

        if demon_core_stacks >= 3 and demonbolt_ready:
            return self.cast(f"target{DEMONBOLT}")

        if hand_ready and soul_shards >= 3 and not dreadstalkers_ready:
            return self.cast(f"target{HAND_OF_GULDAN}")

        if demon_core_stacks >= 1 and demonbolt_ready:
            return self.cast(f"target{DEMONBOLT}")

        if shadow_bolt_ready:
            return self.cast(f"target{SHADOW_BOLT}")

        return self.idle("当前没有合适动作")

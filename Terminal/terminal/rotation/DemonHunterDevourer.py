"""
35魂
天赋：CgcBG5bbocFKcv+yIq8fPd6ORBA2mxMzMzMzMGzMAAAAAAAMmtBDAAAAAAAAmxMMzMzMzMzMzYmNzYsolFmZmZ2abmZGADDABMGMmB
"""

from datetime import datetime

from terminal.context import Context
from .base import BaseRotation


class DemonHunterDevourer(BaseRotation):
    name = "噬灭歼灭者DH"
    desc = "目前只适配歼灭者"

    def __init__(self) -> None:
        super().__init__()
        self._burst_star_count = 0
        self._burst_void_ray_count = 0
        self._last_seen_succeeded_cast = ""

        self.macroTable = {
            "target吞噬": "ALT-NUMPAD1",
            "focus吞噬": "ALT-NUMPAD2",
            "就近吞噬": "ALT-NUMPAD3",
            "target收割": "ALT-NUMPAD4",
            "虚空射线": "ALT-NUMPAD5",
            "target根除": "ALT-NUMPAD6",
            "虚空变形": "ALT-NUMPAD7",
            "target坍缩之星": "ALT-NUMPAD8",
            "target瓦解": "ALT-NUMPAD9",
            "focus瓦解": "ALT-NUMPAD0",
            "疾影": "SHIFT-NUMPAD1",
            "灵魂献祭": "SHIFT-NUMPAD2",
            "鲁莽药水": "SHIFT-NUMPAD3",
            "停止施法": "SHIFT-NUMPAD4",
            "治疗石": "SHIFT-NUMPAD5",
            "强效治疗药水": "SHIFT-NUMPAD6",
            "威厄高尔的最终凝视": "SHIFT-NUMPAD7",
            "飞逝鲁莽药水": "SHIFT-NUMPAD8",
        }

    def main_rotation(self, ctx: Context) -> tuple[str, float, str]:

        if not ctx.enable:
            return self.idle("总开关未开启")

        if ctx.delay:
            return self.idle("延迟开关开启")

        spell_queue_window = float(ctx.spell_queue_window or 0.3)
        player = ctx.player
        target = ctx.target
        focus = ctx.focus
        mouseover = ctx.mouseover
        latest_succeeded_cast = ctx.latest_succeeded_cast

        # ── 设置项读取 ──────────────────────────────────────────────

        # AOE敌人数量阈值 min:2 max:10 default:4 step:1
        aoe_enemy_count_cell = ctx.setting.cell(5)
        aoe_enemy_count = (
            4 if aoe_enemy_count_cell is None else round(aoe_enemy_count_cell.mean / 10)
        )

        # 灵魂碎片（玩家身上）
        soul_fragments_cell = ctx.spec.cell(0)
        soul_fragments = (
            0 if soul_fragments_cell is None else int(soul_fragments_cell.mean / 5)
        )

        # 获取恶魔之怒最大值，默认120，恶魔之怒是根据这个值来计算的。因为不同版本恶魔之怒的最大值可能不同，所以让用户自己设置这个值。
        fury_max = 120
        fury = int(ctx.player.powerPercent * fury_max / 100)

        # 斩杀血量阈值（默认10%）
        reaper_health_threshold_cell = ctx.setting.cell(4)
        reaper_health_threshold = (
            10
            if reaper_health_threshold_cell is None
            else int(reaper_health_threshold_cell.mean)
        )

        # 打断模式（blacklist / any）
        dh_interrupt_mode_cell = ctx.setting.cell(1)
        dh_interrupt_mode = (
            "blacklist"
            if dh_interrupt_mode_cell is None or dh_interrupt_mode_cell.mean >= 200
            else "any"
        )
        interrupt_blacklist = ctx.interrupt_blacklist
        spell_stop_list = ctx.spell_stop_list
        range_spell_stop_list = ctx.range_spell_stop_list

        # 躺平模式（turn_on / turn_off）
        lying_flat_mode_cell = ctx.setting.cell(0)
        lying_flat_mode = (
            "turn_off"
            if lying_flat_mode_cell is None or lying_flat_mode_cell.mean >= 200
            else "turn_on"
        )

        # 开启保命血量阈值（默认60%）
        # 爆发药开关（turn_on / turn_off），默认关闭
        use_burst_potion_cell = ctx.setting.cell(6)
        use_burst_potion = (
            "turn_off"
            if use_burst_potion_cell is None or use_burst_potion_cell.mean >= 200
            else "turn_on"
        )

        dh_health_threshold_cell = ctx.setting.cell(2)
        dh_health_threshold = (
            60
            if dh_health_threshold_cell is None
            else int(dh_health_threshold_cell.mean)
        )

        # 虚空变形阈值（常态，默认35）
        void_metamorphosis_threshold_cell = ctx.setting.cell(3)
        void_metamorphosis_threshold = (
            35
            if void_metamorphosis_threshold_cell is None
            else int(void_metamorphosis_threshold_cell.mean)
        )

        # 技能队列窗口，施法中剩余时间小于这个值就算技能快要好了，可以提前衔接施放下一个技能，单位是秒
        # 施法保护阈值，剩余施法时间低于此值时不打断当前施法，单位百分比。设为 90 意味着始终等待施法完成（任何技能施法时间都远小于此值）
        cast_queue_window_threshold = 90
        # 引导保护阈值，剩余引导时间低于此值时不打断当前引导，单位是百分比。设为 90 意味着始终等待引导完成
        channel_queue_window_threshold = 90

        # ── 基础状态检查 ────────────────────────────────────────────

        if not player.alive:
            return self.idle("玩家已死亡")

        if player.isChatInputActive:
            return self.idle("正在聊天输入")

        if player.isMounted:
            return self.idle("骑乘中")

        if player.castIcon is not None:
            if (
                player.castDuration is None
                or player.castDuration < cast_queue_window_threshold
            ):
                return self.idle("正在施法")

        if player.channelIcon is not None:
            if (
                player.channelDuration is None
                or player.channelDuration < channel_queue_window_threshold
            ):
                return self.idle("正在引导")

        if player.isEmpowering:
            return self.idle("正在蓄力")

        if player.hasBuff("食物和饮料"):
            return self.idle("正在吃喝")

        if not player.isInCombat:
            return self.idle("未进入战斗")

        # ── 主目标确定 ──────────────────────────────────────────────

        main_enemy = None
        if focus.exists and focus.canAttack and focus.isInRangedRange:
            main_enemy = focus
        elif target.exists and target.canAttack and target.isInRangedRange:
            main_enemy = target

        if main_enemy is None:
            return self.idle("没有合适的目标")

        # ── AOE判断 ─────────────────────────────────────────────────
        is_aoe = player.enemyCount >= aoe_enemy_count

        def cast_devour() -> tuple[str, float, str] | None:
            if main_enemy is focus:
                return self.cast("focus吞噬")
            if main_enemy is target:
                return self.cast("target吞噬")
            if player.enemyCount >= 1:
                return self.cast("就近吞噬")
            return None

        # ── Buff/状态读取 ───────────────────────────────────────────

        # 疾影
        phase_shift_buff_exists = player.hasBuff("疾影")

        # 虚落层数
        voidfall_count = player.buffStack("虚落")

        # 地上的灵魂碎片（散落）
        scattered_souls_fragments_count = player.buffStack("灵魂残片")

        # 噬欲时刻
        moment_of_craving_exists = player.hasBuff("噬欲时刻")
        moment_of_craving_remaining = player.buffRemain("噬欲时刻")

        # 坍缩之星（爆发变身标志）
        collapsing_star_exists = player.hasBuff("坍缩之星")

        if not collapsing_star_exists:
            self._burst_star_count = 0
            self._burst_void_ray_count = 0
            self._last_seen_succeeded_cast = ""
        elif latest_succeeded_cast != self._last_seen_succeeded_cast:
            if latest_succeeded_cast == "坍缩之星":
                self._burst_star_count += 1
            elif latest_succeeded_cast == "虚空射线":
                self._burst_void_ray_count += 1
            self._last_seen_succeeded_cast = latest_succeeded_cast

        # 灵魂献祭
        soul_immolation_exists = player.hasBuff("灵魂献祭")

        # ── 保命：献祭 > 治疗石 > 强效治疗药水 ──────────────────────────
        # 优先级：灵魂献祭 > 治疗石 > 强效治疗药水
        # 任意一个可用则使用并跳过后续检查
        if player.healthPercent < dh_health_threshold:
            # 1. 灵魂献祭（应急，忽略常规优先级限制）
            # 灵魂献祭在持续时间内可回复24%最大生命值
            if not soul_immolation_exists and ctx.spell_cooldown_ready(
                "灵魂献祭", spell_queue_window
            ):
                return self.cast("灵魂献祭")

            # 2. 治疗石player.healthstoneCooldownUsable
            if ctx.spell_cooldown_ready("治疗石", spell_queue_window):
                return self.cast("治疗石")

            # 3. 强效治疗药水player.healingPotionCooldownUsable
            if ctx.spell_cooldown_ready("强效治疗药水", spell_queue_window):
                return self.cast("强效治疗药水")

        # ── 打断逻辑 ────────────────────────────────────────────────

        focus_need_interrupt = False
        target_need_interrupt = False

        if focus.exists and focus.canAttack and focus.isInRangedRange:
            if focus.anyCastIcon is not None and focus.anyCastIsInterruptible:
                if dh_interrupt_mode == "any":
                    focus_need_interrupt = True
                elif focus.anyCastIcon not in interrupt_blacklist:
                    focus_need_interrupt = True

        if target.exists and target.canAttack and target.isInRangedRange:
            if target.anyCastIcon is not None and target.anyCastIsInterruptible:
                if dh_interrupt_mode == "any":
                    target_need_interrupt = True
                elif target.anyCastIcon not in interrupt_blacklist:
                    target_need_interrupt = True

        protected_interrupt_casts = {"虚空射线", "坍缩之星"}
        player_cast_protected = (
            player.castIcon in protected_interrupt_casts
            or player.channelIcon in protected_interrupt_casts
        )

        if not player_cast_protected and ctx.spell_cooldown_ready(
            "瓦解", spell_queue_window, ignore_gcd=True
        ):
            if focus_need_interrupt:
                return self.cast("focus瓦解")
            elif target_need_interrupt:
                return self.cast("target瓦解")

        # ── 停止施法黑名单检查 ──────────────────────────────────────

        trigger_spell = None
        player_need_spell_stop = False
        if target.exists and target.anyCastIcon in spell_stop_list:
            trigger_spell = target.anyCastIcon
            player_need_spell_stop = True
        elif focus.exists and focus.anyCastIcon in spell_stop_list:
            trigger_spell = focus.anyCastIcon
            player_need_spell_stop = True

        if player_need_spell_stop:
            return self.idle(f"检测到黑名单技能 [{trigger_spell}]，停止施法")

        # ── 大范围技能停止施法黑名单检查 ──────────────────────────────

        range_trigger_spell = None
        player_need_specific_spell_stop = False
        if target.exists and target.anyCastIcon in range_spell_stop_list:
            range_trigger_spell = target.anyCastIcon
            player_need_specific_spell_stop = True
        elif focus.exists and focus.anyCastIcon in range_spell_stop_list:
            range_trigger_spell = focus.anyCastIcon
            player_need_specific_spell_stop = True

        can_stand_cast = not player_need_specific_spell_stop and not player.isMoving
        ground_souls_full = scattered_souls_fragments_count >= 10
        body_souls_high = soul_fragments >= 36
        body_souls_safe_for_eradication = soul_fragments <= 30
        feast_stacks = player.buffStack("灵魂盛宴")
        feast_remaining = player.buffRemain("灵魂盛宴")

        star_ready = can_stand_cast and ctx.spell_cooldown_ready(
            "坍缩之星", spell_queue_window
        )
        void_ray_ready = (
            can_stand_cast
            and target.isInRangedRange
            and ctx.spell_cooldown_ready("虚空射线", spell_queue_window)
        )
        eradication_ready = ctx.spell_cooldown_ready("根除", spell_queue_window)
        feast_exists = feast_remaining > 0 or feast_stacks > 0
        feast_eradication_ready = (
            eradication_ready and feast_exists and ground_souls_full
        )
        immolation_ready = not soul_immolation_exists and ctx.spell_cooldown_ready(
            "灵魂献祭", spell_queue_window
        )
        devour_ready = ctx.spell_cooldown_ready("吞噬", spell_queue_window)
        pre_metamorphosis_high_fury = fury >= 70 and fury < 100
        pre_metamorphosis_low_fury = fury < 70 and not ground_souls_full

        # ══════════════════════════════════════════════════════════════
        # 爆发段：前三星虚空射线优先，带 buff 的根除滞后，第四星后按献祭轴处理。
        # ══════════════════════════════════════════════════════════════
        if collapsing_star_exists:

            # ── 躺平模式：变身中停止坍缩之星和根除，堆碎片等退出变身 ────
            if lying_flat_mode == "turn_on":
                # 身上和地上各>=10魂后停手，等待变身自然结束
                if soul_fragments >= 10 and scattered_souls_fragments_count >= 10:
                    return self.idle("躺平模式：碎片已就绪，等待退出变身")

                # 仅使用虚空射线和吞噬来堆碎片
                if (
                    not player_need_specific_spell_stop
                    and not player.isMoving
                    and target.isInRangedRange
                    and ctx.spell_cooldown_ready("虚空射线", spell_queue_window)
                ):
                    return self.cast("虚空射线")

                if ctx.spell_cooldown_ready("吞噬", spell_queue_window):
                    cast_result = cast_devour()
                    if cast_result is not None:
                        return cast_result

                return self.idle("躺平模式：爆发中堆碎片，等待CD")

            # ── 正常爆发逻辑 ────────────────────────────────────────────

            # 变身内已持续时间（秒）
            burst_time = float(ctx.burst_time or 0)
            post_fourth_star = self._burst_star_count >= 4
            late_fury_phase = burst_time >= 35
            can_aim_fifth_star = ground_souls_full or burst_time <= 40
            high_quality_star = is_aoe or feast_stacks >= 20 or ground_souls_full
            feast_ending_soon = feast_remaining > 0 and feast_remaining <= 3
            # 怒气低只表示变身收尾压力变高，不表示坍缩之星需要怒气。
            fifth_star_time_pressure = fury < 55
            delayed_buffed_eradication = feast_eradication_ready and (
                body_souls_safe_for_eradication
                or feast_ending_soon
                or latest_succeeded_cast == "坍缩之星"
            )
            fifth_star_ready = (
                star_ready
                and can_aim_fifth_star
                and (
                    is_aoe
                    or ground_souls_full
                    or body_souls_high
                    or fifth_star_time_pressure
                )
            )
            fifth_star_window = (
                post_fourth_star
                and can_aim_fifth_star
                and (
                    latest_succeeded_cast in {"根除", "威厄高尔的最终凝视"}
                    or ground_souls_full
                    or body_souls_high
                    or fifth_star_time_pressure
                )
            )
            normal_star_ready = star_ready and (
                is_aoe
                or high_quality_star
                or latest_succeeded_cast == "虚空射线"
                or not ground_souls_full
            )
            single_target_feast_opener = (
                not is_aoe and self._burst_star_count == 0 and feast_exists
            )
            single_target_feast_star_ready = (
                single_target_feast_opener and star_ready and feast_stacks >= 15
            )
            single_target_feast_eradication_ready = (
                single_target_feast_opener
                and feast_eradication_ready
                and feast_stacks < 15
            )
            gaze_star_ready = (
                fifth_star_ready if post_fourth_star else normal_star_ready
            )

            # 虚空变形后紧接着使用"鲁莽药水"
            if (
                lying_flat_mode == "turn_off"
                and latest_succeeded_cast == "虚空变形"
                and use_burst_potion == "turn_on"
                # and player.burstPotionCooldownUsable
                # and ctx.gcd_ready(spell_queue_window)
                and ctx.spell_cooldown_ready("鲁莽药水", spell_queue_window)
            ):
                return self.cast("鲁莽药水")

            if latest_succeeded_cast == "威厄高尔的最终凝视":
                if star_ready:
                    return self.cast("target坍缩之星")
                return self.idle("最终凝视后等待坍缩之星")

            if (
                lying_flat_mode == "turn_off"
                and ctx.spell_cooldown_ready("威厄高尔的最终凝视", spell_queue_window)
                and gaze_star_ready
            ):
                return self.cast("威厄高尔的最终凝视")

            # 第四颗星后：献祭 -> 多扣吞噬 -> 半怒虚空射线回怒 -> 根除接星。
            if post_fourth_star:
                if fifth_star_ready:
                    return self.cast("target坍缩之星")

                if (
                    player.enemyCount <= 5
                    and latest_succeeded_cast == "坍缩之星"
                    and immolation_ready
                    and (ground_souls_full or fury <= 60)
                ):
                    return self.cast("灵魂献祭")

                if void_ray_ready and (fury <= 65 or late_fury_phase):
                    return self.cast("虚空射线")

                if delayed_buffed_eradication:
                    return self.cast("target根除")

                if fifth_star_window:
                    return self.idle("五星窗口：等待坍缩之星")

                if (
                    devour_ready
                    and fury > 60
                    and (not ground_souls_full or soul_fragments < 40)
                ):
                    cast_result = cast_devour()
                    if cast_result is not None:
                        return cast_result

            # 前三星：未带盛宴进变身时虚空射线优先；带盛宴时按层数先星或根除。
            if single_target_feast_star_ready:
                return self.cast("target坍缩之星")

            if single_target_feast_eradication_ready:
                return self.cast("target根除")

            if self._burst_star_count < 3 and void_ray_ready:
                return self.cast("虚空射线")

            if delayed_buffed_eradication:
                return self.cast("target根除")

            if normal_star_ready:
                return self.cast("target坍缩之星")

            if void_ray_ready and (late_fury_phase or fury <= 70):
                return self.cast("虚空射线")

            if devour_ready:
                cast_result = cast_devour()
                if cast_result is not None:
                    return cast_result

            return self.idle("爆发中：等待CD")

        # ══════════════════════════════════════════════════════════════
        # 常态/暖机：主动献祭 -> 吞噬攒怒 -> 100 怒虚空射线 -> 根除，准备进变身。
        # ══════════════════════════════════════════════════════════════

        if immolation_ready:
            return self.cast("灵魂献祭")

        if feast_eradication_ready:
            return self.cast("target根除")

        if void_ray_ready:
            return self.cast("虚空射线")

        if voidfall_count >= 3:
            if feast_eradication_ready:
                return self.cast("target根除")
            if ctx.spell_cooldown_ready("收割", spell_queue_window):
                return self.cast("target收割")

        if (
            lying_flat_mode == "turn_off"
            and ctx.spell_cooldown_ready("虚空变形", spell_queue_window)
            and main_enemy.healthPercent > reaper_health_threshold
            and not player.isMoving
        ):
            metamorphosis_after_void_ray = latest_succeeded_cast == "虚空射线"
            if pre_metamorphosis_low_fury:
                return self.cast("虚空变形")
            if pre_metamorphosis_high_fury and devour_ready:
                return cast_devour()
            if metamorphosis_after_void_ray:
                return self.cast("虚空变形")

        if devour_ready:
            cast_result = cast_devour()
            if cast_result is not None:
                return cast_result

        return self.idle("当前没有合适动作")

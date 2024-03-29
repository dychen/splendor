import random


class IllegalMove(Exception):
    pass


class GameState():
    __WIN_POINTS = 15
    __TIERS = [1, 2, 3]
    __TIER_SIZE = 4
    __GEMS = ['w', 'u', 'g', 'r', 'b']
    __P_GEM_LIMIT = 10
    __T2_GEM_LIMIT = 4
    __GOLD_LIMIT = 5
    __P_RESERVE_LIMIT = 3
    __NUM_NOBLES = 4

    def __load_cards(self):
        d = { t: [] for t in self.__TIERS }
        with open('gamedata.tsv') as f:
            for line in f:
                t, w_c, u_c, g_c, r_c, b_c, v, p = line.strip().split('\t')
                d[int(t)].append([int(w_c), int(u_c), int(g_c), int(r_c), int(b_c), v, int(p)])
        return d

    def __load_nobles(self):
        nobles = []
        with open('nobledata.tsv') as f:
            for line in f:
                w_c, u_c, g_c, r_c, b_c, p = line.strip().split('\t')
                nobles.append([int(w_c), int(u_c), int(g_c), int(r_c), int(b_c), int(p)])
        return nobles

    def __shuffle_cards(self):
        """Mutates state"""
        for _, cards in self.cards.items():
            random.shuffle(cards)

    def __draw_and_replace(self, src_card_list, dest_card_list):
        try:
            new_card = src_card_list.pop(0)
            dest_card_list.append(new_card)
        except IndexError:
            print('No more cards in deck')
            return

    def __draw_initial(self):
        board = { t: [] for t in self.__TIERS }
        for t in self.__TIERS:
            for _ in range(self.__TIER_SIZE):
                self.__draw_and_replace(self.cards[t], board[t])
        return board

    def __draw_nobles(self):
        nobles = self.__load_nobles()
        random.shuffle(nobles)
        return nobles[:self.__NUM_NOBLES]

    def __initialize_gems(self, num_players):
        n = 7
        if num_players == 2:
            n = 4
        elif num_players == 3:
            n = 5
        return [n for _ in range(len(self.__GEMS))]

    def __initialize_players(self, num_players):
        return { i: { 'gems': [0, 0, 0, 0, 0], 'cards': [], 'nobles': [],
                      'reserved': [], 'gold': 0 }
                 for i in range(num_players) }

    def __init__(self, num_players=2):
        """
        self.cards: { [tier]: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]] }
        self.board: { [tier]: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]] }
        self.nobles: [[w_cost, u_cost, g_cost, r_cost, b_cost, points]]
        self.gems: [w_count, u_count, g_count, r_count, b_count]
        self.gold: 5
        self.players: { [player]: {
            gems: [w_count, u_count, g_count, r_count, b_count],
            cards: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]],
            nobles: [[w_cost, u_cost, g_cost, r_cost, b_cost, points]],
            reserved: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]],
            gold: 0
        }}
        """
        self.cards = self.__load_cards()
        self.__shuffle_cards()
        self.board = self.__draw_initial()
        self.nobles = self.__draw_nobles()
        self.gems = self.__initialize_gems(num_players)
        self.gold = self.__GOLD_LIMIT
        self.players = self.__initialize_players(num_players)
        self.meta = {
            'num_players': num_players,
            'turn': 1,
            'is_last_turn': False
        }

    def get_points(self, player):
        return (sum([x[-1] for x in self.players[player]['cards']])
                + sum([x[-1] for x in self.players[player]['nobles']]))

    def get_total_gems(self, player):
        return [x + y for x, y in zip(self.players[player]['gems'], self.get_card_gems(player))]

    def get_card_gems(self, player):
        indices = [self.__GEMS.index(x[5]) for x in self.players[player]['cards']]
        return [indices.count(i) for i in range(len(self.__GEMS))]

    def __check_player_gem_count(self, player, data):
        if not (sum(self.players[player]['gems']) + sum(data) <= self.__P_GEM_LIMIT):
            raise IllegalMove('Player would exceed 10 gems')

    def __check_board_gem_count(self, player, data):
        if not (len([True for x, y in zip(self.gems, data) if x - y < 0]) == 0):
            raise IllegalMove('Gem stack would go below zero')

    def __check_take_3_valid(self, player, data):
        if not (len(data) == 5 and set(data) == set([0, 1]) and sum(data) <= 3):
            raise IllegalMove('Invalid take 3 input')

    def __check_take_2_valid(self, player, data):
        if not (len(data) == 5 and set(data) == set([0, 2]) and data.count(2) == 1):
            raise IllegalMove('Invalid take 2 input')

    def __check_take_2_stack_size(self, player, data):
        if not (self.gems[data.index(2)] >= self.__T2_GEM_LIMIT):
            raise IllegalMove('Stack too low to take 2 gems')

    def __check_reserve_valid(self, data):
        if len(data) != 2 or not data[0] in self.board:
            raise IllegalMove('Invalid reserve input')

    def __check_board_gold_count(self):
        if not (self.gold > 0):
            raise IllegalMove('Gold stack would go below zero')

    def __check_player_reserve_count(self, player):
        if not (len(self.players[player]['reserved']) < self.__P_RESERVE_LIMIT):
            raise IllegalMove('Player has already reserved the max amount of cards')

    def __check_buy_from_board_valid(self, data):
        if len(data) != 2 or not data[0] in self.board:
            raise IllegalMove('Invalid buy from board input')

    def __check_buy_from_reserve_valid(self, data):
        if len(data) != 1:
            raise IllegalMove('Invalid buy from reserve input')

    def __check_card_exists(self, card_list, index):
        try:
            card_list[index]
        except IndexError:
            raise IllegalMove('Target card doesn\'t exist')

    def __check_player_can_buy(self, player, target_costs):
        """Player can buy if sum(max_each(costs - pgems, 0)) <= player_gold"""
        if not (sum([max(x - y, 0) for x, y in zip(target_costs, self.get_total_gems(player))])
                <= self.players[player]['gold']):
            raise IllegalMove('Not enough gems to buy card')

    def move_take_3(self, player, data):
        self.__check_take_3_valid(player, data)
        self.__check_board_gem_count(player, data)
        self.__check_player_gem_count(player, data)
        for i in range(len(data)):
            self.gems[i] -= data[i]
            self.players[player]['gems'][i] += data[i]

    def move_take_2(self, player, data):
        self.__check_take_2_valid(player, data)
        self.__check_board_gem_count(player, data)
        self.__check_player_gem_count(player, data)
        self.__check_take_2_stack_size(player, data)
        for i in range(len(data)):
            self.gems[i] -= data[i]
            self.players[player]['gems'][i] += data[i]

    def move_reserve(self, player, data):
        self.__check_reserve_valid(data)
        self.__check_board_gold_count()
        self.__check_player_reserve_count(player)
        tier, index = data
        card_list = self.board[tier]
        self.__check_card_exists(card_list, index)
        # Take and draw
        card = card_list.pop(index)
        self.players[player]['reserved'].append(card)
        self.__draw_and_replace(self.cards[tier], card_list)
        # Take gold
        self.players[player]['gold'] += 1

    def can_buy(self, card_list, index, player):
        self.__check_card_exists(card_list, index)
        target = card_list[index]
        self.__check_player_can_buy(player, target[:5])
        return target

    def move_buy(self, player, tier, index, from_reserve):
        def pay(card):
            # Number of gems the player needs to spend without gold
            cost_arr = [max(x - y, 0) for x, y in zip(card[:5], self.get_card_gems(player))]
            new_pgems = [x - y for x, y in zip(self.players[player]['gems'], cost_arr)]
            gold_rebate = [abs(min(x, 0)) for x in new_pgems]
            gold_cost = sum(gold_rebate)
            # Number of gems the player needs to spend with gold
            cost_arr2 = [x - y for x, y in zip(cost_arr, gold_rebate)]
            new_pgems2 = [x - y for x, y in zip(self.players[player]['gems'], cost_arr2)]
            assert(sum([x - y for x, y in zip(cost_arr, cost_arr2)]) == gold_cost)
            # Update player state
            self.players[player]['gems'] = new_pgems2
            self.players[player]['gold'] -= gold_cost
            # Update board state
            self.gems = [x + y for x, y in zip(self.gems, cost_arr2)]
            self.gold += gold_cost
        def take(card_list, index):
            card = card_list.pop(index)
            self.players[player]['cards'].append(card)
        def noble_visit():
            player_card_gems = self.get_card_gems(player)
            to_remove_indices = []
            for i, noble in enumerate(self.nobles):
                # If noble gem cost - player card gem <= 0 for each gem
                if sum([max(x - y, 0) for x, y in zip(noble[:5], player_card_gems)]) == 0:
                    to_remove_indices.append(i)
                    self.players[player]['nobles'].append(noble)
            self.nobles = [noble for i, noble in enumerate(self.nobles)
                           if i not in to_remove_indices]

        if from_reserve:
            card_list = self.players[player]['reserved']
            card = self.can_buy(card_list, index, player)
            pay(card)
            take(card_list, index)
        else:
            card_list = self.board[tier]
            card = self.can_buy(card_list, index, player)
            pay(card)
            take(card_list, index)
            self.__draw_and_replace(self.cards[tier], card_list)
        noble_visit()

    def move_buy_from_board(self, player, data):
        self.__check_buy_from_board_valid(data)
        tier, index = data
        self.move_buy(player, tier, index, False)

    def move_buy_from_reserve(self, player, data):
        self.__check_buy_from_reserve_valid(data)
        index, = data # Deconstruct list of size 1
        self.move_buy(player, None, index, True)

    def move(self, player, action, data):
        if action == 't3':
            self.move_take_3(player, data)
            print('>> Player {} took 3 gems: {}'.format(player, data))
        elif action == 't2':
            self.move_take_2(player, data)
            print('>> Player {} took 2 gems: {}'.format(player, data))
        elif action == 'r':
            self.move_reserve(player, data)
            print('>> Player {} reserved a card: {}'.format(player, data))
        elif action == 'b':
            self.move_buy_from_board(player, data)
            print('>> Player {} bought a card from the board: {}'.format(player, data))
        elif action == 'br':
            self.move_buy_from_reserve(player, data)
            print('>> Player {} bought a card from the reserve: {}'.format(player, data))
        else:
            raise IllegalMove('Invalid action - must be one of [t3/t2/r/b/br]')

    def __print_player_state(self, i):
        pstate = self.players[i]
        print('=PLAYER {}='.format(i))
        print('  POINTS: {}'.format(self.get_points(i)))
        print('  NORM GEMS: {} GOLD: {}'.format(pstate['gems'], pstate['gold']))
        print('  CARD GEMS: {}'.format(self.get_card_gems(i)))
        print('  TOTL GEMS: {} GOLD: {}'.format(self.get_total_gems(i), pstate['gold']))
        for card in pstate['cards']:
            print('    CARD: {}'.format(card))
        for card in pstate['reserved']:
            print('    RESERVED: {}'.format(card))
        for card in pstate['nobles']:
            print('    NOBLE: {}'.format(card))

    def print_state(self):
        print('=====NEW STATE=====')
        for tier, bstate in self.board.items():
            print('=TIER {}='.format(tier))
            for card in bstate:
                print(card)
        print('=NOBLES=')
        for noble in self.nobles:
            print(noble)
        print('=GEMS=')
        print(self.gems)
        for i, _ in self.players.items():
            self.__print_player_state(i)
        print('========END========')

    def check_last_turn(self):
        for i, pstate in self.players.items():
            if self.get_points(i) >= self.__WIN_POINTS:
                return True
        return False

    def print_results(self):
        # Sort by: 1. most number of points 2. reverse player order 3. least number of cards
        sorted_players = sorted([
            (i, self.get_points(i), len(self.players[i]['cards']))
            for i, pstate in self.players.items()
        ], key=lambda x: (-x[1], -x[0], x[2]))
        for i, t in enumerate(sorted_players):
            pindex, _, _ = t
            print('==RANK {}: PLAYER {}=='.format(i+1, pindex))
            self.__print_player_state(i)
        print('!!!WINNER: PLAYER {}!!!'.format(sorted_players[0][0]))

    def print_possible_buys(self, player):
        print('=POSSIBLE BUYS:=')
        for card_list, name in ([(self.players[player]['reserved'], 'Reserved')]
                                + [(self.board[tier], 'Tier {}'.format(tier))
                                   for tier in self.__TIERS]):
            for i in range(len(card_list)):
                try:
                    card = self.can_buy(card_list, i, player)
                    print(name, i, card)
                except IllegalMove:
                    continue

    def run(self):
        def make_move(i):
            try:
                print('==PLAYER ' + str(i) + '==')
                self.print_possible_buys(i)
                move_arr = raw_input('Move? [t3/t2/r/b/br] [data]: ').strip().split(' ')
                action, data = move_arr[0], [int(x) for x in move_arr[1:]]
                self.move(i, action, data)
                self.print_state()
            except IllegalMove as e:
                print('==ILLEGAL MOVE: {}=='.format(e))
                make_move(i)

        self.print_state()
        while not self.meta['is_last_turn']:
            print('\n\n==TURN ' + str(self.meta['turn']) + '==')
            for i in range(self.meta['num_players']):
                make_move(i)
                if self.check_last_turn():
                    print('=LAST TURN, PLAYER {} HAS {} POINTS='.format(i, self.get_points(i)))
                    self.meta['is_last_turn'] = True
            self.meta['turn'] += 1
        self.print_results()

GameState().run()

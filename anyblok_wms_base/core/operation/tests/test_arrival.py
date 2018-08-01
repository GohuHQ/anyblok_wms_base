# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / WMS Base project
#
#    Copyright (C) 2018 Georges Racinet <gracinet@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from .testcase import WmsTestCase


class TestArrival(WmsTestCase):

    def setUp(self):
        super(TestArrival, self).setUp()
        Goods = self.Goods
        self.goods_type = Goods.Type.insert(label="My good type",
                                            code='MGT')
        self.incoming_loc = self.insert_location('INCOMING')
        self.stock = self.insert_location('STOCK')

        self.Arrival = self.Operation.Arrival
        self.Avatar = self.Goods.Avatar

    def test_create_planned_execute(self):
        arrival = self.Arrival.create(location=self.incoming_loc,
                                      state='planned',
                                      dt_execution=self.dt_test1,
                                      goods_code='765',
                                      goods_properties=dict(foo=5,
                                                            bar='monty'),
                                      goods_type=self.goods_type)
        self.assertEqual(arrival.follows, [])
        avatar = self.assert_singleton(arrival.outcomes)
        goods = avatar.goods
        self.assertEqual(avatar.state, 'future')
        self.assertEqual(avatar.location, self.incoming_loc)
        self.assertEqual(goods.type, self.goods_type)
        self.assertEqual(goods.code, '765')
        self.assertEqual(goods.get_property('foo'), 5)
        self.assertEqual(goods.get_property('bar'), 'monty')
        self.assertEqual(avatar.dt_from, self.dt_test1)

        arrival.execute(self.dt_test2)
        self.assertEqual(arrival.state, 'done')
        self.assertEqual(arrival.dt_execution, self.dt_test2)
        self.assertEqual(arrival.dt_start, self.dt_test2)
        self.assertEqual(avatar.state, 'present')
        self.assertEqual(goods.get_property('foo'), 5)
        self.assertEqual(goods.get_property('bar'), 'monty')
        self.assertEqual(goods.code, '765')
        self.assertEqual(avatar.dt_from, self.dt_test2)

    def test_create_done(self):
        arrival = self.Arrival.create(location=self.incoming_loc,
                                      state='done',
                                      goods_code='x34/7',
                                      goods_properties=dict(foo=2,
                                                            monty='python'),
                                      goods_type=self.goods_type)
        self.assertEqual(arrival.follows, [])
        avatar = self.assert_singleton(arrival.outcomes)
        goods = avatar.goods
        self.assertEqual(avatar.state, 'present')
        self.assertEqual(avatar.location, self.incoming_loc)
        self.assertEqual(goods.type, self.goods_type)
        self.assertEqual(goods.code, 'x34/7')
        self.assertEqual(goods.get_property('foo'), 2)
        self.assertEqual(goods.get_property('monty'), 'python')

    def test_arrival_done_obliviate(self):
        arrival = self.Arrival.create(location=self.incoming_loc,
                                      state='done',
                                      goods_code='x34/7',
                                      goods_properties=dict(foo=2,
                                                            monty='python'),
                                      goods_type=self.goods_type)
        arrival.obliviate()
        self.assertEqual(self.Avatar.query().count(), 0)
        self.assertEqual(
            self.Goods.query().filter_by(type=self.goods_type).count(), 0)

    def test_arrival_planned_execute_obliviate(self):
        arrival = self.Arrival.create(location=self.incoming_loc,
                                      state='planned',
                                      dt_execution=self.dt_test1,
                                      goods_code='x34/7',
                                      goods_properties=dict(foo=2,
                                                            monty='python'),
                                      goods_type=self.goods_type)
        arrival.execute()
        arrival.obliviate()
        self.assertEqual(self.Avatar.query().count(), 0)
        self.assertEqual(
            self.Goods.query().filter_by(type=self.goods_type).count(), 0)

    def test_repr(self):
        arrival = self.Arrival(location=self.incoming_loc,
                               state='done',
                               goods_code='x34/7',
                               goods_properties=dict(foo=2,
                                                     monty='python'),
                               goods_type=self.goods_type)
        repr(arrival)
        str(arrival)


class TestOperationBase(WmsTestCase):
    """Test the Operation base class

    In these test cases, Operation.Move is considered the canonical example
    to test some corner cases in the base Operation model.
    """

    def setUp(self):
        super(TestOperationBase, self).setUp()
        Goods = self.Goods
        self.goods_type = Goods.Type.insert(code='MGT')
        self.incoming_loc = self.insert_location("Incoming")
        self.stock = self.insert_location("Stock")

        self.Arrival = self.Operation.Arrival

    def test_execute_idempotency(self):
        op = self.Arrival.create(location=self.incoming_loc,
                                 state='planned',
                                 dt_execution=self.dt_test2,
                                 goods_type=self.goods_type)
        op.state = 'done'
        op.execute_planned = lambda: self.fail("Should not be called")
        op.execute()

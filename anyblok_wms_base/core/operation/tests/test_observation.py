# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / WMS Base project
#
#    Copyright (C) 2018 Georges Racinet <gracinet@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_wms_base.testing import WmsTestCaseWithPhysObj


class TestObservation(WmsTestCaseWithPhysObj):

    def setUp(self):
        super(TestObservation, self).setUp()
        self.Observation = self.Operation.Observation

    def test_planned_execute(self):
        obs = self.Observation.create(state='planned',
                                      dt_execution=self.dt_test2,
                                      input=self.avatar)

        self.assertEqual(obs.follows, [self.arrival])
        self.assertEqual(obs.input, self.avatar)
        self.assertEqual(self.avatar.dt_until, self.dt_test2)
        outcome = self.assert_singleton(obs.outcomes)

        self.assertEqual(outcome.dt_from, self.dt_test2)
        self.assertIsNone(outcome.dt_until)

        self.avatar.state = 'present'
        obs.observed_properties = dict(qa='ok')
        obs.execute(self.dt_test3)

        self.assertEqual(obs.state, 'done')
        self.assertEqual(self.goods.get_property('qa'), 'ok')
        self.assertEqual(self.avatar.state, 'past')
        self.assertEqual(outcome.state, 'present')

    def test_done(self):
        self.avatar.state = 'present'
        obs = self.Observation.create(state='done',
                                      observed_properties=dict(qa='ok'),
                                      dt_execution=self.dt_test2,
                                      input=self.avatar)

        self.assertEqual(obs.follows, [self.arrival])
        self.assertEqual(obs.input, self.avatar)
        self.assertEqual(obs.state, 'done')

        self.assertEqual(self.goods.get_property('qa'), 'ok')
        self.assertEqual(self.avatar.dt_until, self.dt_test2)
        self.assertEqual(self.avatar.state, 'past')

        outcome = self.assert_singleton(obs.outcomes)
        self.assertEqual(outcome.dt_from, self.dt_test2)
        self.assertIsNone(outcome.dt_until)
        self.assertEqual(outcome.state, 'present')

    def test_repr(self):
        dep = self.Observation.create(state='planned',
                                      dt_execution=self.dt_test2,
                                      input=self.avatar)
        repr(dep)
        str(dep)


del WmsTestCaseWithPhysObj

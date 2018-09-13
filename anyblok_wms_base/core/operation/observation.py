# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / WMS Base project
#
#    Copyright (C) 2018 Georges Racinet <gracinet@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer
from anyblok_postgres.column import Jsonb

register = Declarations.register
Mixin = Declarations.Mixin
Operation = Declarations.Model.Wms.Operation


@register(Operation)
class Observation(Mixin.WmsSingleInputOperation, Operation):
    """Operation to change PhysObj Properties.

    Besides being commonly associated with some measurement or assessment
    being done in reality, this Operation is the preferred way to alter the
    Properties of a physical object (PhysObj), in a traceable, reversible way.

    For now, only whole Property values are supported, i.e., for
    :class:`dict`-valued Properties, we can't observe the value of just a
    subkey.

    .. note:: Like most non destructive Operations, an Observation always
              creates a new Avatar. This may see superflous, but it is
              actually useful to navigate in operational history in an
              uniform way. Also having at some point different states for
              these two avatars is useful, e.g., to insist on the Observation
              being done before subsequent Operations etc.
    """
    TYPE = 'wms_observation'

    id = Integer(label="Identifier",
                 primary_key=True,
                 autoincrement=False,
                 foreign_key=Operation.use('id').options(ondelete='cascade'))
    """Primary key."""

    observed_properties = Jsonb()
    """Result of the Observation.

    It is forbidden to fill this field for a planned Observation.

    TODO: rethink this, wouldn't it make sense actually to record some
    expected results, so that dependent Operations could be themselves planned
    ? This doesn't seem to be that useful, since e.g., Assemblies can check
    different Properties according to their progress.

    Another case would be for reversals: prefill the result.
    """

    previous_properties = Jsonb()
    """Used in particular during oblivion.

    TODO and maybe reversal
    """

    def after_insert(self):
        inp_av = self.input
        physobj = inp_av.obj
        state = self.state
        if state != 'done' and self.observed_properties is not None:
            # TODO precise exc
            raise ValueError("Forbidden create a planned or just started "
                             "Observation together with its results")
        dt_exec = self.dt_execution
        physobj.Avatar.insert(
            obj=physobj,
            state='future' if state == 'planned' else 'present',
            reason=self,
            location=self.input.location,
            dt_from=dt_exec,
            dt_until=None)

        inp_av.update(dt_until=dt_exec, state='past')

        if self.state == 'done':
            self.apply_properties()

    def apply_properties(self):
        # TODO save previous properties (the direct ones, not the merged
        # version)
        observed = self.observed_properties
        if observed is None:
            # TODO precise exc
            raise ValueError("Can't execute with no observed properties")
        self.input.obj.update_properties(observed)

    def execute_planned(self):
        self.apply_properties()
        dt_exec = self.dt_execution
        self.input.update(dt_until=dt_exec, state='past')
        self.outcomes[0].update(dt_from=dt_exec, state='present', reason=self)

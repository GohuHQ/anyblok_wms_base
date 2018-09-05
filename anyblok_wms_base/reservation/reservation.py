# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / WMS Base project
#
#    Copyright (C) 2018 Georges Racinet <gracinet@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import warnings

from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from anyblok import Declarations
from anyblok.column import Integer
from anyblok.relationship import Many2One

register = Declarations.register
Wms = Declarations.Model.Wms


def deprecation_warn_goods():
        warnings.warn("The 'goods' attribute of Model.Wms.Reservation.Avatar "
                      "is deprecated, please rename to 'obj' before "
                      "version 1.0 of Anyblok / WMS Base",
                      DeprecationWarning,
                      stacklevel=2)


@register(Wms)
class Reservation:

    physobj = Many2One(model=Wms.PhysObj, primary_key=True, index=True)
    quantity = Integer()
    """The quantity that this Reservation provides.

    If the PhysObj in the application have ``quantity`` field
    (see :ref:`improvement_no_quantities`), this is not necessarily its value
    within :attr:`goods`. Instead, it is the quantity within the
    :attr:`request_item` that the current Reservation provides.

    Use-case some PhysObj being sold either as packs of 10 or by
    the unit. If one wants to reserve 13 of them,
    it should be expressable as one pack of 10 and 3 units.
    Then maybe (depending on the needs), would it be actually
    smarter of the application to not issue an Unpack.
    """
    request_item = Many2One(model=Wms.Reservation.RequestItem,
                            index=True)

    @hybrid_property
    def goods(self):
        """Compatibility wrapper.

        Before the merge of Goods and Locations as PhysObj, :attr:`physobj` was
        ``goods``.

        Same trick does not work for ``goods_id`` though, probably because
        this implicit column does not exist yet during registry load.
        TODO ask jssuzanne about that and maybe introduce Anyblok's
        hybrid_property besides hybrid_method
        """
        deprecation_warn_goods()
        return self.physobj

    @goods.setter
    def goods(self, value):
        deprecation_warn_goods()
        self.physobj = value

    @classmethod
    def define_table_args(cls):
        return super(Reservation, cls).define_table_args() + (
            CheckConstraint('quantity > 0', name='positive_qty'),
        )

    def is_transaction_owner(self):
        """Check that the current transaction is the owner of the reservation.
        """
        return self.request_item.request.is_txn_reservations_owner()

    def is_transaction_allowed(self, opcls, state, dt_execution,
                               inputs=None, **kwargs):
        """TODO add allowances, like a Move not far."""
        return self.is_transaction_owner()

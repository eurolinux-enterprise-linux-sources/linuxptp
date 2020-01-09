/**
 * @file phc.h
 * @note Copyright (C) 2011 Richard Cochran <richardcochran@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
#ifndef HAVE_PHC_H
#define HAVE_PHC_H

#include "missing.h"

/**
 * Opens a PTP hardware clock device.
 *
 * @param phc The device to open.
 *
 * @return A valid clock ID on success, CLOCK_INVALID otherwise.
 */
clockid_t phc_open(char *phc);

/**
 * Closes a PTP hardware clock device.
 *
 * @param clkid A clock ID obtained using phc_open().
 */
void phc_close(clockid_t clkid);

/**
 * Query the maximum frequency adjustment of a PTP hardware clock device.
 *
 * @param clkid A clock ID obtained using phc_open().
 *
 * @return The clock's maximum frequency adjustment in parts per billion.
 */
int phc_max_adj(clockid_t clkid);

#endif

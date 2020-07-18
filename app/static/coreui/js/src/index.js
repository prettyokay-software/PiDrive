import $ from 'jquery'
import AjaxLoad from './ajax-load'
import AsideMenu from './aside-menu'
import Sidebar from './sidebar'

/**
 * --------------------------------------------------------------------------
 * CoreUI (v2.0.0-beta.2): index.js
 * Licensed under MIT (https://coreui.io/license)
 * --------------------------------------------------------------------------
 */

(($) => {
  if (typeof $ === 'undefined') {
    throw new TypeError('CoreUI\'s JavaScript requires jQuery. jQuery must be included before CoreUI\'s JavaScript.')
  }

  const version = $.fn.jquery.split(' ')[0].split('.')
  const minMajor = 1
  const ltMajor = 2
  const minMinor = 9
  const minPatch = 1
  const maxMajor = 4

  if (version[0] < ltMajor && version[1] < minMinor || version[0] === minMajor && version[1] === minMinor && version[2] < minPatch || version[0] >= maxMajor) {
    throw new Error('CoreUI\'s JavaScript requires at least jQuery v1.9.1 but less than v4.0.0')
  }
})($)

export {
  AjaxLoad,
  AsideMenu,
  Sidebar
}

// Global functions
import GetStyle from './utilities/get-style'
window.GetStyle = GetStyle

import HexToRgb from './utilities/hex-to-rgb'
window.HexToRgb = HexToRgb

import HexToRgba from './utilities/hex-to-rgba'
window.HexToRgba = HexToRgba

import RgbToHex from './utilities/rgb-to-hex'
window.RgbToHex = RgbToHex

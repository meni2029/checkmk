<!--
Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->

<!--
	ATTENTION: this is not a general building, only use as part of CmkDropdown
-->

<script setup lang="ts">
import { useTemplateRef } from 'vue'
import CmkButton from './CmkButton.vue'
import { type VariantProps, cva } from 'class-variance-authority'

export interface ButtonProps {
  group?: ButtonVariants['group']
}

const buttonVariants = cva('', {
  variants: {
    group: {
      no: '',
      start: 'cmk-dropdown-button--group-start',
      end: 'cmk-dropdown-button--variant-group-end'
    },
    width: {
      default: '',
      wide: 'wide'
    }
  },
  defaultVariants: {
    group: 'no'
  }
})

export type ButtonVariants = VariantProps<typeof buttonVariants>

const {
  disabled = false,
  multipleChoicesAvailable = true,
  valueIsSelected = true
} = defineProps<{
  disabled?: boolean
  multipleChoicesAvailable?: boolean
  valueIsSelected?: boolean
  group?: ButtonVariants['group']
  width?: ButtonVariants['width']
}>()

const button = useTemplateRef<InstanceType<typeof CmkButton>>('button')

defineExpose({
  focus: () => {
    button.value?.focus()
  }
})
</script>

<template>
  <CmkButton
    ref="button"
    role="combobox"
    class="cmk-dropdown-button"
    :class="[
      buttonVariants({ group, width }),
      {
        disabled,
        no_choices: !multipleChoicesAvailable,
        no_value: !valueIsSelected
      }
    ]"
  >
    <slot />
  </CmkButton>
</template>

<style scoped>
.cmk-dropdown-button {
  height: var(--form-field-height);
  margin: 0;
  padding: 3px 6px 4px 6px;
  vertical-align: baseline;
  background-color: var(--default-form-element-bg-color);
  border: none;
  justify-content: space-between;
  font-weight: var(--font-weight-default);
  cursor: pointer;

  &.wide {
    min-width: 10em;
  }

  &:hover {
    background-color: var(--input-hover-bg-color);
  }

  &.disabled {
    cursor: auto;
    color: var(--font-color-dimmed);
    &:hover {
      background-color: var(--default-form-element-bg-color);
    }
  }

  &.no_value {
    color: var(--font-color-dimmed);

    > .cmk-dropdown-button_arrow {
      color: var(--font-color);
    }
  }

  &.no_choices {
    cursor: auto;
    &:hover {
      background-color: var(--default-form-element-bg-color);
    }
    > .cmk-dropdown-button_arrow {
      opacity: 0.4;
    }
  }

  &.cmk-dropdown-button--group-start {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }

  &.cmk-dropdown-button--variant-group-end {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
}
</style>

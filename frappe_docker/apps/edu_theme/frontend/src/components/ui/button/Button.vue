<script setup lang="ts">
import { Primitive, type PrimitiveProps } from 'radix-vue'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-semibold ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary-dark shadow-md hover:shadow-lg rounded-lg',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 rounded-lg',
        outline: 'border-2 border-primary text-primary bg-transparent hover:bg-primary hover:text-primary-foreground rounded-lg',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-lg',
        ghost: 'hover:bg-accent hover:text-accent-foreground rounded-lg',
        link: 'text-primary underline-offset-4 hover:underline',
        hero: 'bg-primary text-primary-foreground hover:bg-primary-dark shadow-lg hover:shadow-xl rounded-lg',
        heroOutline: 'border-2 border-primary-foreground text-primary-foreground bg-transparent hover:bg-primary-foreground/10 rounded-lg',
        accent: 'bg-accent text-accent-foreground hover:bg-accent/90 shadow-md hover:shadow-lg rounded-lg',
        nav: 'text-primary-foreground/90 hover:text-primary-foreground hover:bg-primary-foreground/10 font-medium rounded-lg',
      },
      size: {
        default: 'h-10 px-6 py-2',
        sm: 'h-9 px-4',
        lg: 'h-12 px-8 text-base',
        xl: 'h-14 px-10 text-lg',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

interface Props extends PrimitiveProps {
  variant?: VariantProps<typeof buttonVariants>['variant']
  size?: VariantProps<typeof buttonVariants>['size']
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  as: 'button',
})
</script>

<template>
  <Primitive
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </Primitive>
</template>

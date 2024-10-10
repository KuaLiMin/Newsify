/*
This is for the homepage (shop)
*/
import React from 'react'
import Trending from '../components/Trending/Trending'
import Hero from '../components/Hero/Hero'
import Browse from '../components/Listing/Browse'

export const Categories = () => {
  return (
    <div>
      <Hero/>
      <Trending.TrendingCounter />     

    </div>
  )
}
export default Categories
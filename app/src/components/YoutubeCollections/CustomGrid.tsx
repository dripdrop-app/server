import React, { useState } from 'react';
import { Grid } from '@mui/material';

const CustomGrid = <T,>(props: { items: T[]; renderItem: (item: T, selected: boolean) => JSX.Element }) => {
	const [hoveredItem, setHoveredItem] = useState(-1);

	return (
		<Grid container spacing={2}>
			{props.items.map((item, i) => {
				return (
					<Grid
						onMouseEnter={() => setHoveredItem(i)}
						onMouseLeave={() => setHoveredItem(-1)}
						item
						xs={4}
						md={3}
						key={i}
					>
						{props.renderItem(item, hoveredItem === i)}
					</Grid>
				);
			})}
		</Grid>
	);
};

export default CustomGrid;

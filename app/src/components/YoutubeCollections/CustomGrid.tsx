import React, { useState } from 'react';
import { Grid } from '@mui/material';

const CustomGrid = <T,>(props: { items: T[]; renderItem: (item: T) => JSX.Element }) => {
	const [hoveredItem, setHoveredItem] = useState(-1);

	return (
		<Grid container spacing={2}>
			{props.items.map((item, i) => {
				return (
					<Grid
						sx={{ transform: hoveredItem === i ? 'scale(1.1)' : '' }}
						onMouseEnter={() => setHoveredItem(i)}
						onMouseLeave={() => setHoveredItem(-1)}
						item
						xs={4}
						md={3}
						key={i}
					>
						{props.renderItem(item)}
					</Grid>
				);
			})}
		</Grid>
	);
};

export default CustomGrid;

import React, { useCallback, useEffect, useState, useRef } from 'react';
import { Box, Fab } from '@mui/material';
import { ArrowUpward } from '@mui/icons-material';
import ConditionalDisplay from './ConditionalDisplay';

interface InfiniteScrollProps<T> {
	items: T[];
	renderItem: (item: T, index: number) => JSX.Element | JSX.Element[];
	onEndReached?: () => void;
}

const InfiniteScroll = <T,>(props: InfiniteScrollProps<T>) => {
	const { items, renderItem, onEndReached } = props;
	const [showScrollButton, setShowScrollButton] = useState(false);

	const boxRef = useRef<HTMLDivElement>();

	const onGridBottom = useCallback(() => {
		if (document.body.offsetHeight - 500 < window.innerHeight + window.scrollY && onEndReached) {
			onEndReached();
		}
	}, [onEndReached]);

	const updateScrollButton = useCallback(() => {
		if (boxRef.current) {
			const grid = boxRef.current;
			const gridCoordinates = grid.getBoundingClientRect();
			if (gridCoordinates.y < 0 && !showScrollButton) {
				setShowScrollButton(true);
			} else if (gridCoordinates.y > 0 && showScrollButton) {
				setShowScrollButton(false);
			}
		}
	}, [showScrollButton]);

	useEffect(() => {
		window.addEventListener('scroll', updateScrollButton);
		window.addEventListener('scroll', onGridBottom);
		return () => {
			window.removeEventListener('scroll', onGridBottom);
			window.removeEventListener('scroll', updateScrollButton);
		};
	}, [onGridBottom, updateScrollButton]);

	return (
		<Box>
			<Box ref={boxRef}>
				{items.map((item, index) => (
					<React.Fragment key={`scroll-item-${index}`}>{renderItem(item, index)}</React.Fragment>
				))}
			</Box>
			<ConditionalDisplay condition={showScrollButton}>
				<Box
					sx={{
						position: 'fixed',
						right: '5vw',
						bottom: '10vh',
					}}
				>
					<Fab
						variant="circular"
						color="primary"
						onClick={() => {
							if (boxRef.current) {
								window.scrollTo({ top: boxRef.current.offsetTop - 100, behavior: 'smooth' });
							}
						}}
					>
						<ArrowUpward />
					</Fab>
				</Box>
			</ConditionalDisplay>
		</Box>
	);
};

export default InfiniteScroll;

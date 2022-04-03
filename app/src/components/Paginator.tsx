import { Box, Pagination } from '@mui/material';

interface PaginatorProps {
	isFetching: boolean;
	page: number;
	pageCount: number;
	onChange: (newPage: number) => void;
}

const Paginator = (props: PaginatorProps) => {
	const { isFetching, page, pageCount, onChange } = props;
	if (!isFetching) {
		return (
			<Box>
				<Box display={{ md: 'none' }}>
					<Pagination siblingCount={0} page={page} count={pageCount} onChange={(e, data) => onChange(data)} />
				</Box>
				<Box display={{ xs: 'none', md: 'block' }}>
					<Pagination page={page} count={pageCount} onChange={(e, data) => onChange(data)} />
				</Box>
			</Box>
		);
	}
	return null;
};

export default Paginator;

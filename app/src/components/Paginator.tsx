import { Pagination, useTheme, useMediaQuery } from '@mui/material';

interface PaginatorProps {
	isFetching: boolean;
	page: number;
	pageCount: number;
	onChange: (newPage: number) => void;
}

const Paginator = (props: PaginatorProps) => {
	const { isFetching, page, pageCount, onChange } = props;

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	if (!isFetching) {
		return (
			<Pagination
				siblingCount={isSmall ? 0 : undefined}
				page={page}
				count={pageCount}
				onChange={(e, data) => onChange(data)}
			/>
		);
	}
	return null;
};

export default Paginator;

import React, { useMemo } from 'react';
import { CircularProgress, Stack } from '@mui/material';
import { useCheckYoutubeAuthQuery } from '../../api/youtube';

interface YoutubeWrapperProps {
	children: JSX.Element;
	altRender?: JSX.Element;
	showLoading?: boolean;
}

const YoutubeWrapper = (props: YoutubeWrapperProps) => {
	const youtubeAuthStatus = useCheckYoutubeAuthQuery();

	return useMemo(() => {
		if (youtubeAuthStatus.isFetching && props.showLoading) {
			return (
				<Stack padding={10} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (
			youtubeAuthStatus.isSuccess &&
			youtubeAuthStatus.currentData &&
			youtubeAuthStatus.currentData.email &&
			!youtubeAuthStatus.currentData.refresh
		) {
			return React.cloneElement(props.children, { youtubeuser: youtubeAuthStatus.currentData });
		}
		return props.altRender ?? null;
	}, [props, youtubeAuthStatus.currentData, youtubeAuthStatus.isFetching, youtubeAuthStatus.isSuccess]);
};

export default YoutubeWrapper;

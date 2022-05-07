import { useEffect, useMemo, useRef, useState } from 'react';
import { isEqual, pick } from 'lodash';
import { useYoutubeVideosQuery } from '../api/youtube';

export const useYoutubeVideos = (args: YoutubeVideosBody, argsToMatch: Partial<YoutubeVideosBody>) => {
	const [videoMap, setVideoMap] = useState<VideoMap>({});
	const queryMatchArgs = useRef(argsToMatch);

	const videosStatus = useYoutubeVideosQuery(args);

	const videos = useMemo(
		() =>
			Object.keys(videoMap)
				.sort()
				.flatMap((page) => videoMap[parseInt(page)]),
		[videoMap]
	);

	useEffect(() => {
		if (!isEqual(argsToMatch, queryMatchArgs)) {
			queryMatchArgs.current = argsToMatch;
		}
	}, [argsToMatch]);

	useEffect(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			const newVideos = videosStatus.currentData.videos;
			if (videosStatus.originalArgs) {
				const calledArgs = pick(videosStatus.originalArgs, Object.keys(queryMatchArgs.current));
				if (isEqual(queryMatchArgs.current, calledArgs)) {
					setVideoMap((videoMap) => {
						return { ...videoMap, [args.page]: newVideos };
					});
				}
			}
		}
	}, [args.page, videosStatus.currentData, videosStatus.isSuccess, videosStatus.originalArgs]);

	return useMemo(() => ({ videos, videoMap, videosStatus, setVideoMap }), [videoMap, videos, videosStatus]);
};
